"""Tools to help getting selenium and widgetastic browser instance to run UI
tests.
"""
import base64
import logging
import os
import time
import urllib
from datetime import datetime
from urllib.parse import unquote

import selenium
from fauxfactory import gen_string
from selenium import webdriver
from wait_for import wait_for
from widgetastic.browser import Browser
from widgetastic.browser import DefaultPlugin

from airgun import settings

try:
    import docker
except ImportError:
    # Let it fail later if not installed
    docker = None

try:
    import sauceclient
except ImportError:
    # Optional requirement, airgun will report results back to saucelabs if
    # installed
    sauceclient = None


LOGGER = logging.getLogger(__name__)


class DockerBrowserError(Exception):
    """Indicates any issue with DockerBrowser."""


def _sauce_ondemand_url(saucelabs_user, saucelabs_key):
    """Get sauce ondemand URL for a given user and key.

    :param str saucelabs_user: saucelabs username
    :param str saucelabs_key: saucelabs access key
    :return: string representing saucelabs ondemand URL
    """
    return 'http://{0}:{1}@ondemand.saucelabs.com:80/wd/hub'.format(
        saucelabs_user, saucelabs_key)


class SeleniumBrowserFactory(object):
    """Factory which creates selenium browser of desired provider (selenium,
    docker or saucelabs). Creates all required capabilities, passes certificate
    checks and applies other workarounds. It is also capable of finalizing the
    browser when it's not needed anymore (closes the browser, stops docker
    container, sends test results to saucelabs etc).

    Usage::

        # init factory
        factory = SeleniumBrowserFactory(test_name=test_name)

        # get factory browser
        selenium_browser = factory.get_browser()

        # navigate to desired url
        # [...]

        # perform post-init steps (e.g. skipping certificate error screen)
        factory.post_init()

        # perform your test steps
        # [...]

        # perform factory clean-up
        factory.finalize(passed)

    """

    def __init__(self, provider=None, browser=None, test_name=None, session_cookie=None):
        """Initializes factory with either specified or fetched from settings
        values.

        :param str optional provider: Browser provider name. One of
            ('selenium', 'docker', 'saucelabs', 'remote'). If none specified -
            :attr:`settings.selenium.browser` is used.
        :param str optional browser: Browser name. One of ('chrome', 'firefox',
            'ie', 'edge', 'phantomjs'). Not required for ``docker``
            provider as it currently supports firefox only. If none specified -
            :attr:`settings.selenium.webdriver` is used.
        :param str optional test_name: Name of the test using this factory. It
            is useful for `saucelabs` provider to update saucelabs job name, or
            for `docker` provider to create container with meaningful name, not
            used otherwise.
        :param requests.sessions.Session optional session_cookie: session object to be used
            to bypass login
        """
        self.provider = provider or settings.selenium.browser
        self.browser = browser or settings.selenium.webdriver
        self.test_name = test_name
        self._session = session_cookie
        self._docker = None
        self._webdriver = None

    def get_browser(self):
        """Returns selenium webdriver instance of selected ``provider`` and
        ``browser``.

        :return: selenium webdriver instance
        :raises: ValueError: If wrong ``provider`` or ``browser`` specified.
        """
        if self.provider == 'selenium':
            return self._get_selenium_browser()
        elif self.provider == 'saucelabs':
            return self._get_saucelabs_browser()
        elif self.provider == 'docker':
            return self._get_docker_browser()
        elif self.provider == 'remote':
            return self._get_remote_browser()
        else:
            raise ValueError(
                '"{}" browser is not supported. Please use one of {}'
                .format(
                    self.provider,
                    ('selenium', 'saucelabs', 'docker', 'remote')
                )
            )

    def post_init(self):
        """Perform all required post-init tweaks and workarounds. Should be
        called _after_ proceeding to desired url.

        :return: None
        """
        # Workaround 'Certificate Error' screen on Microsoft Edge
        if (
                self.browser == 'edge' and
                ('Certificate Error' in self._webdriver.title or
                    'Login' not in self._webdriver.title)):
            self._webdriver.get(
                "javascript:document.getElementById('invalidcert_continue')"
                ".click()"
            )
        # Workaround maximize_window() not working with chrome in docker
        if not (self.provider == 'docker' and
                self.browser == 'chrome'):
            self._webdriver.maximize_window()

    def finalize(self, passed=True):
        """Finalize browser - close browser window, report results to saucelabs
        or close docker container if needed.

        :param bool passed: Boolean value indicating whether test passed
            or not. Is only used for ``saucelabs`` provider.
        :return: None
        """
        if self.provider == 'selenium' or self.provider == 'remote':
            self._webdriver.quit()
            return
        elif self.provider == 'saucelabs':
            self._webdriver.quit()
            return self._finalize_saucelabs_browser(passed)
        elif self.provider == 'docker':
            return self._finalize_docker_browser()

    def _set_session_cookie(self):
        """Add the session cookie (if provided) to the webdriver
        """
        if self._session:
            # webdriver doesn't allow to add cookies unless we land on the target domain
            # let's navigate to its invalid page to get it loaded ASAP
            self._webdriver.get('https://{0}/404'.format(settings.satellite.hostname))
            self._webdriver.add_cookie(
                {'name': '_session_id', 'value': self._session.cookies.get_dict()['_session_id']}
            )

    def _get_selenium_browser(self):
        """Returns selenium webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        kwargs = {}
        binary = settings.selenium.webdriver_binary
        browseroptions = settings.selenium.browseroptions

        if self.browser == 'chrome':
            if binary:
                kwargs.update({'executable_path': binary})
            options = webdriver.ChromeOptions()
            prefs = {'download.prompt_for_download': False}
            options.add_experimental_option("prefs", prefs)
            options.add_argument('disable-web-security')
            if browseroptions:
                for opt in browseroptions.split(';'):
                    options.add_argument(opt)
            kwargs.update({'options': options})
            self._webdriver = webdriver.Chrome(**kwargs)
        elif self.browser == 'firefox':
            if binary:
                kwargs.update({'executable_path': binary})
            self._webdriver = webdriver.Firefox(**kwargs)
        elif self.browser == 'ie':
            if binary:
                kwargs.update({'executable_path': binary})
            self._webdriver = webdriver.Ie(**kwargs)
        elif self.browser == 'edge':
            if binary:
                kwargs.update({'executable_path': binary})
            capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['javascriptEnabled'] = True
            kwargs.update({'capabilities': capabilities})
            self._webdriver = webdriver.Edge(**kwargs)
        elif self.browser == 'phantomjs':
            self._webdriver = webdriver.PhantomJS(
                service_args=['--ignore-ssl-errors=true'])
        if self._webdriver is None:
            raise ValueError(
                '"{}" webdriver is not supported. Please use one of {}'
                .format(
                    self.browser,
                    ('chrome', 'firefox', 'ie', 'edge', 'phantomjs')
                )
            )
        self._set_session_cookie()
        return self._webdriver

    def _get_saucelabs_browser(self):
        """Returns saucelabs webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        self._webdriver = webdriver.Remote(
            command_executor=_sauce_ondemand_url(
                settings.selenium.saucelabs_user,
                settings.selenium.saucelabs_key
            ),
            desired_capabilities=self._get_webdriver_capabilities()
        )
        self._set_session_cookie()
        idle_timeout = settings.webdriver_desired_capabilities.idleTimeout
        if idle_timeout:
            self._webdriver.command_executor.set_timeout(int(idle_timeout))
        return self._webdriver

    def _get_docker_browser(self):
        """Returns webdriver running in docker container. Currently only
        firefox and chrome are supported.

        Note: should not be called directly, use :meth:`get_browser` instead.
        """
        kwargs = {}
        if self.test_name:
            kwargs.update({'name': self.test_name})
        self._docker = DockerBrowser(**kwargs)
        if self.browser == 'chrome':
            self._docker._image = 'selenium/standalone-chrome'
            self._docker._capabilities = \
                webdriver.DesiredCapabilities.CHROME.copy()
            self._docker._capabilities.update({'args': 'start-maximized'})
        elif self.browser == 'firefox':
            self._docker._image = 'selenium/standalone-firefox'
            self._docker._capabilities = \
                webdriver.DesiredCapabilities.FIREFOX.copy()
        else:
            raise ValueError(
                '"{}" webdriver in docker container is currently not'
                'supported. Please use one of {}'
                .format(self.browser, ('chrome', 'firefox'))
            )
        if settings.webdriver_desired_capabilities:
            self._docker._capabilities.update(
                vars(settings.webdriver_desired_capabilities))
        self._docker.start()
        self._webdriver = self._docker.webdriver
        self._set_session_cookie()
        return self._webdriver

    def _get_remote_browser(self):
        """Returns remote webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.
        """
        self._webdriver = webdriver.Remote(
            command_executor=settings.selenium.command_executor,
            desired_capabilities=self._get_webdriver_capabilities()
        )
        self._set_session_cookie()

        idle_timeout = settings.webdriver_desired_capabilities.idleTimeout
        if idle_timeout:
            self._webdriver.command_executor.set_timeout(int(idle_timeout))
        return self._webdriver

    def _get_webdriver_capabilities(self):
        """Returns webdriver capabilities of selected ``browser``.

        Note: should not be called directly, use :meth:`_get_remote_browser`
        or :meth:`_get_saucelabs_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        if self.browser == 'chrome':
            desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            enable_downloading = {
                'chromeOptions': {
                    'args': ['disable-web-security'],
                    'prefs': {'download.prompt_for_download': False}
                }
            }
            desired_capabilities.update(enable_downloading)
        elif self.browser == 'firefox':
            desired_capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
        elif self.browser == 'ie':
            desired_capabilities = (
                webdriver.DesiredCapabilities.INTERNETEXPLORER.copy())
        elif self.browser == 'edge':
            desired_capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            desired_capabilities['acceptSslCerts'] = True
            desired_capabilities['javascriptEnabled'] = True
        else:
            raise ValueError(
                '"{}" webdriver capabilities is currently not supported. '
                'Please use one of {}'
                .format(self.browser, ('chrome', 'firefox', 'ie', 'edge'))
            )
        if settings.webdriver_desired_capabilities:
            desired_capabilities.update(
                vars(settings.webdriver_desired_capabilities))

        desired_capabilities.update({'name': self.test_name})

        return desired_capabilities

    def _finalize_saucelabs_browser(self, passed):
        """SauceLabs has no way to determine whether test passed or failed
        automatically, so we explicitly 'tell' it.

        Note: should not be called directly, use :meth:`finalize` instead.

        :param bool passed: Bool value indicating whether test passed or not.
        """
        client = sauceclient.SauceClient(
            settings.selenium.saucelabs_user, settings.selenium.saucelabs_key)
        LOGGER.debug(
            'Updating SauceLabs job "%s": name "%s" and status "%s"',
            self._webdriver.session_id,
            self.test_name,
            'passed' if passed else 'failed'
        )
        kwargs = {'passed': passed}
        # do not pass test name if it's not set
        if self.test_name:
            kwargs.update({'name': self.test_name})
        client.jobs.update_job(self._webdriver.session_id, **kwargs)

    def _finalize_docker_browser(self):
        """Stops docker container.

        Note: should not be called directly, use :meth:`finalize` instead.
        """
        self._docker.stop()


class DockerBrowser(object):
    """Provide a browser instance running inside a docker container.

    Usage::

        # either as context manager
        with DockerBrowser() as browser:
            # [...]

        # or with manual :meth:`start` and :meth:`stop` calls.
        docker_browser = DockerBrowser()
        docker_browser.start()
        # [...]
        docker_browser.stop()

    """

    def __init__(self, name=None, image=None, capabilities=None):
        """Ensure ``docker-py`` package is installed.

        :param str optional name: name for docker container.
        :raises: airgun.browser.DockerBrowserError: if ``docker-py`` package is
            not installed.
        """
        if docker is None:
            raise DockerBrowserError(
                'Package docker-py is not installed. Install it in order to '
                'use DockerBrowser.'
            )
        self.webdriver = None
        self._capabilities = capabilities
        self._image = image
        self.container = None
        self._client = None
        self._name = name or gen_string('alphanumeric')
        self._started = False

    def start(self):
        """Start all machinery needed to run a browser inside a docker
        container.
        """
        if self._started:
            return
        self._init_client()
        self._create_container()
        self._init_webdriver()
        self._started = True

    def stop(self):
        """Quit the browser, remove docker container and close docker client.
        """
        self._quit_webdriver()
        self._remove_container()
        self._close_client()
        self.webdriver = None
        self.container = None
        self._client = None
        self._started = False

    def _init_webdriver(self):
        """Init the selenium Remote webdriver."""
        if self.webdriver or not self.container:
            return
        exception = None
        # An exception can be raised while the container is not ready
        # yet. Give up to 10 seconds for a container being ready.
        for _ in range(20):
            try:
                self.webdriver = webdriver.Remote(
                    command_executor='http://127.0.0.1:{0}/wd/hub'.format(
                        self.container['HostPort']),
                    desired_capabilities=self._capabilities
                )
            except Exception as err:
                # Capture the raised exception for later usage and wait
                # a few for the next attempt.
                exception = err
                time.sleep(.5)
            else:
                # Connection succeeded time to leave the for loop
                break
        else:
            # Reraise the captured exception.
            raise DockerBrowserError(
                'Failed to connect the webdriver to the containerized '
                'selenium.'
            ) from exception

    def _quit_webdriver(self):
        """Quit the selenium remote webdriver."""
        if not self.webdriver:
            return
        self.webdriver.quit()

    def _init_client(self):
        """Init docker client.

        Make sure that docker service to be published under the
        ``unix://var/run/docker.sock`` unix socket.

        Use auto for version in order to allow docker client to automatically
        figure out the server version.
        """
        if self._client:
            return
        self._client = docker.Client(
            base_url='unix://var/run/docker.sock', version='auto')

    def _close_client(self):
        """Close docker Client."""
        if not self._client:
            return
        self._client.close()

    def _create_container(self):
        """Create a docker container running a ``standalone-firefox`` or
        ``standalone-chrome`` selenium.

        Make sure to have the image ``selenium/standalone-firefox`` or
        ``selenium/standalone-chrome`` already pulled, preferably in the
        same version as the selenium-module.
        """
        if self.container:
            return
        image_version = selenium.__version__
        if not self._client.images(
                name=self._get_image_name(image_version)):
            LOGGER.warning('Could not find docker-image for your'
                           'selium-version "%s"; trying with "latest"',
                           self._get_image_name(image_version))
            image_version = 'latest'
            if not self._client.images(
                    name=self._get_image_name(image_version)):
                raise DockerBrowserError(
                    'Could not find docker-image "%s"; please pull it' %
                    self._get_image_name(image_version)
                )
        # Grab only the test name, get rid of square brackets from parametrize
        # and add some random chars. E.g. 'test_positive_create_0_abc'
        container_name = '{}_{}'.format(
            self._name.split('.')[-1].replace('[', '_').strip(']'),
            gen_string('alphanumeric', 3)
        )
        self.container = self._client.create_container(
            detach=True,
            environment={
                'SCREEN_WIDTH': '1920',
                'SCREEN_HEIGHT': '1080',
            },
            host_config=self._client.create_host_config(
                publish_all_ports=True),
            image=self._get_image_name(image_version),
            name=container_name,
            ports=[4444],
        )
        LOGGER.debug('Starting container with ID "%s"', self.container['Id'])
        self._client.start(self.container['Id'])
        self.container.update(
            self._client.port(self.container['Id'], 4444)[0])

    def _remove_container(self):
        """Turn off and clean up container from system."""
        if not self.container:
            return
        LOGGER.debug('Stopping container with ID "%s"', self.container['Id'])
        self._client.stop(self.container['Id'])
        self._client.wait(self.container['Id'])
        self._client.remove_container(self.container['Id'], force=True)

    def __enter__(self):
        """Setup docker browser when used as context manager."""
        self.start()
        return self

    def __exit__(self, *exc):
        """Perform all cleanups when used as context manager."""
        self.stop()

    def _get_image_name(self, version):
        """Returns docker-image's name and version (aka tag)"""
        return '%s:%s' % (self._image, version)


class AirgunBrowserPlugin(DefaultPlugin):
    """Plug-in for :class:`AirgunBrowser` which adds satellite-specific
    JavaScript to make sure page is loaded completely. Checks for absence of
    jQuery, AJAX, Angular requests, absence of spinner indicating loading
    progress and ensures ``document.readyState`` is "complete".
    """

    ENSURE_PAGE_SAFE = '''
        function jqueryInactive() {
         return (typeof jQuery === "undefined") ? true : jQuery.active < 1
        }
        function ajaxInactive() {
         return (typeof Ajax === "undefined") ? true :
            Ajax.activeRequestCount < 1
        }
        function angularNoRequests() {
         if (typeof angular === "undefined") {
           return true
         } else if (typeof angular.element(
             document).injector() === "undefined") {
           injector = angular.injector(["ng"]);
           return injector.get("$http").pendingRequests.length < 1
         } else {
           return angular.element(document).injector().get(
             "$http").pendingRequests.length < 1
         }
        }
        function spinnerInvisible() {
         spinner = document.getElementById("vertical-spinner")
         return (spinner === null) ? true : spinner.style["display"] == "none"
        }
        function reactLoadingInvisible() {
         react = document.querySelector("#reactRoot .loading-state")
         return react === null
        }
        function anySpinnerInvisible() {
         spinners = Array.prototype.slice.call(
          document.querySelectorAll('.spinner')
          ).filter(function (item,index) {
            return item.offsetWidth > 0 || item.offsetHeight > 0
             || item.getClientRects().length > 0;
           }
          );
         return spinners.length === 0
        }
        return {
            jquery: jqueryInactive(),
            ajax: ajaxInactive(),
            angular: angularNoRequests(),
            spinner: spinnerInvisible(),
            any_spinner: anySpinnerInvisible(),
            react: reactLoadingInvisible(),
            document: document.readyState == "complete",
        }
        '''

    def ensure_page_safe(self, timeout='30s'):
        """Ensures page is fully loaded.
        Default timeout was 10s, this changes it to 30s.
        """
        super().ensure_page_safe(timeout)

    def before_click(self, element, locator=None):
        """Invoked before clicking on an element. Ensure page is fully loaded
        before clicking.
        """
        self.ensure_page_safe()

    def after_click(self, element, locator=None):
        """Invoked after clicking on an element. Ensure page is fully loaded
        before proceeding further.
        """
        # plugin.ensure_page_safe() is invoked from browser click.
        # we should not invoke it a second time, this can conflict with
        # ignore_ajax=True usage from browser click
        pass


class AirgunBrowser(Browser):
    """A wrapper around :class:`widgetastic.browser.Browser` which injects
    :class:`airgun.session.Session` and :class:`AirgunBrowserPlugin`.
    """

    def __init__(self, selenium, session, extra_objects=None):
        """Pass webdriver instance, session and other extra objects (if any).

        :param selenium: :class:`selenium.webdriver.remote.webdriver.WebDriver`
            instance.
        :param session: :class:`airgun.session.Session` instance.
        :param extra_objects: any extra objects you want to include.
        """
        extra_objects = extra_objects or {}
        extra_objects.update({'session': session})
        super(AirgunBrowser, self).__init__(
            selenium,
            plugin_class=AirgunBrowserPlugin,
            extra_objects=extra_objects)
        self.window_handle = selenium.current_window_handle

    def get_client_datetime(self):
        """Make Javascript call inside of browser session to get exact current
        date and time. In that way, we will be isolated from any issue that can
        happen due different environments where test automation code is
        executing and where browser session is opened. That should help us to
        have successful run for docker containers or separated virtual machines
        When calling .getMonth() you need to add +1 to display the correct
        month. Javascript count always starts at 0, so calling .getMonth() in
        May will return 4 and not 5.

        :return: Datetime object that contains data for current date and time
            on a client
        """
        script = ('var currentdate = new Date(); return ({0} + "-" + {1} + '
                  '"-" + {2} + " : " + {3} + ":" + {4});').format(
            'currentdate.getFullYear()',
            '(currentdate.getMonth()+1)',
            'currentdate.getDate()',
            'currentdate.getHours()',
            'currentdate.getMinutes()',
        )
        client_datetime = self.execute_script(script)
        return datetime.strptime(client_datetime, '%Y-%m-%d : %H:%M')

    def get_downloads_list(self):
        """Open browser's downloads screen and return a list of downloaded
        files.

        :return: list of strings representing file URIs
        """
        if settings.selenium.webdriver != 'chrome':
            raise NotImplementedError('Currently only chrome is supported')
        downloads_uri = 'chrome://downloads'
        if not self.url.startswith(downloads_uri):
            self.url = downloads_uri
        return self.execute_script("""
            return downloads.Manager.get().items_
              .filter(e => e.state === "COMPLETE")
              .map(e => e.file_url || e.fileUrl);
        """)

    def get_file_content(self, uri):
        """Get file content by its URI from browser's downloads page.

        :return: bytearray representing file content
        :raises Exception: when error code instead of file content received
        """
        # See https://stackoverflow.com/a/47164044/3552063
        if settings.selenium.webdriver != 'chrome':
            raise NotImplementedError('Currently only chrome is supported')
        elem = self.selenium.execute_script(
            "var input = window.document.createElement('INPUT'); "
            "input.setAttribute('type', 'file'); "
            "input.onchange = function (e) { e.stopPropagation() }; "
            "return window.document.documentElement.appendChild(input); "
        )

        # it must be local absolute path, without protocol
        elem.send_keys(unquote(uri[7:]))

        result = self.selenium.execute_async_script(
            "var input = arguments[0], callback = arguments[1]; "
            "var reader = new FileReader(); "
            "reader.onload = function (ev) { callback(reader.result) }; "
            "reader.onerror = function (ex) { callback(ex.message) }; "
            "reader.readAsDataURL(input.files[0]); "
            "input.remove(); ",
            elem)

        if not result.startswith('data:'):
            raise Exception("Failed to get file content: %s" % result)

        return base64.b64decode(result[result.find('base64,') + 7:])

    def save_downloaded_file(self, file_uri=None, save_path=None):
        """Save local or remote browser's automatically downloaded file to
        specified local path. Useful when you don't know exact file name or
        path where file was downloaded or you're using remote driver with no
        access to worker's filesystem (e.g. saucelabs).

        Usage example::

            view.widget_which_triggers_file_download.click()
            path = self.browser.save_downloaded_file()
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # process file contents


        :param str optional file_uri: URI of file. If not specified - browser's
            latest downloaded file will be selected
        :param str optional save_path: local path where the file should be
            saved. If not specified - ``temp_dir`` from airgun settings will be
            used in case of remote session or just path to saved file in case
            local one.
        """
        current_url = self.url
        files, _ = wait_for(
            self.browser.get_downloads_list,
            timeout=60,
            delay=1,
        )
        if not file_uri:
            file_uri = files[0]
        if (not save_path and settings.selenium.browser == 'selenium'):
            # if test is running locally, there's no need to save the file once
            # again except when explicitly asked to
            file_path = urllib.parse.unquote(
                urllib.parse.urlparse(file_uri).path)
        else:
            if not save_path:
                save_path = settings.airgun.tmp_dir
            content = self.get_file_content(file_uri)
            filename = urllib.parse.unquote(os.path.basename(file_uri))
            with open(os.path.join(save_path, filename), 'wb') as f:
                f.write(content)
            file_path = os.path.join(save_path, filename)
        self.url = current_url
        self.plugin.ensure_page_safe()
        return file_path
