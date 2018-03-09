"""Tools to help getting selenium and widgetastic browser instance to run UI
tests.
"""
import logging
import time

import six

from fauxfactory import gen_string
from selenium import webdriver
from widgetastic.browser import Browser, DefaultPlugin

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

    def __init__(self, provider=None, browser=None, test_name=None):
        """Initializes factory with either specified or fetched from settings
        values.

        :param str optional provider: Browser provider name. One of
            ('selenium', 'docker', 'saucelabs'). If none specified -
            :attr:`settings.selenium.browser` is used.
        :param str optional browser: Browser name. One of ('chrome', 'firefox',
            'ie', 'edge', 'phantomjs', 'remote'). Not required for ``docker``
            provider as it currently supports firefox only. If none specified -
            :attr:`settings.selenium.webdriver` is used.
        :param str optional test_name: Name of the test using this factory. It
            is useful for `saucelabs` provider to update saucelabs job name, or
            for `docker` provider to create container with meaningful name, not
            used otherwise.
        """
        self.provider = provider or settings.selenium.browser
        self.browser = browser or settings.selenium.webdriver
        self.test_name = test_name
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
        else:
            raise ValueError(
                '"{}" browser is not supported. Please use one of {}'
                .format(self.provider, ('selenium', 'saucelabs', 'docker'))
            )

    def post_init(self):
        """Perform all required post-init tweaks and workarounds. Should be
        called _after_ proceeding to desired url.

        :return: None
        """
        # Workaround 'Certificate Error' screen on Microsoft Edge
        if (
                self.browser == 'edge' and
                'Certificate Error' in self._webdriver.title or
                'Login' not in self._webdriver.title):
            self._webdriver.get(
                "javascript:document.getElementById('invalidcert_continue')"
                ".click()"
            )

    def finalize(self, passed=True):
        """Finalize browser - close browser window, report results to saucelabs
        or close docker container if needed.

        :param bool passed: Boolean value indicating whether test passed
            or not. Is only used for ``saucelabs`` provider.
        :return: None
        """
        if self.provider == 'selenium':
            self._webdriver.quit()
            return
        elif self.provider == 'saucelabs':
            self._webdriver.quit()
            return self._finalize_saucelabs_browser(passed)
        elif self.provider == 'docker':
            return self._finalize_docker_browser()

    def _get_selenium_browser(self):
        """Returns selenium webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        kwargs = {}
        binary = settings.selenium.webdriver_binary

        if self.browser == 'chrome':
            if binary:
                kwargs.update({'executable_path': binary})
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
        elif self.browser == 'remote':
            self._webdriver = webdriver.Remote()
        if self._webdriver is None:
            raise ValueError(
                '"{}" webdriver is not supported. Please use one of {}'
                .format(
                    self.provider,
                    ('chrome', 'firefox', 'ie', 'edge', 'phantomjs', 'remote')
                )
            )
        return self._webdriver

    def _get_saucelabs_browser(self):
        """Returns saucelabs webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        if self.browser == 'chrome':
            desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            if settings.webdriver_desired_capabilities:
                desired_capabilities.update(
                    vars(settings.webdriver_desired_capabilities))
        elif self.browser == 'firefox':
            desired_capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
            if settings.webdriver_desired_capabilities:
                desired_capabilities.update(
                    vars(settings.webdriver_desired_capabilities))
        elif self.browser == 'ie':
            desired_capabilities = (
                webdriver.DesiredCapabilities.INTERNETEXPLORER.copy())
            if settings.webdriver_desired_capabilities:
                desired_capabilities.update(
                    vars(settings.webdriver_desired_capabilities))
        elif self.browser == 'edge':
            desired_capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            desired_capabilities['acceptSslCerts'] = True
            desired_capabilities['javascriptEnabled'] = True
            if settings.webdriver_desired_capabilities:
                desired_capabilities.update(
                    vars(settings.webdriver_desired_capabilities))
        else:
            raise ValueError(
                '"{}" webdriver on saucelabs is currently not supported. '
                'Please use one of {}'
                .format(self.provider, ('chrome', 'firefox', 'ie', 'edge'))
            )

        self._webdriver = webdriver.Remote(
            command_executor=_sauce_ondemand_url(
                settings.selenium.saucelabs_user,
                settings.selenium.saucelabs_key
            ),
            desired_capabilities=desired_capabilities
        )
        # todo: attempt to rename job here
        return self._webdriver

    def _get_docker_browser(self):
        """Returns webdriver running in docker container. Currently only
        firefox is supported.

        Note: should not be called directly, use :meth:`get_browser` instead.
        """
        kwargs = {}
        if self.test_name:
            kwargs.update({'name': self.test_name})
        self._docker = DockerBrowser(**kwargs)
        self._docker.start()
        self._webdriver = self._docker.webdriver
        return self._webdriver

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

    def __init__(self, name=None):
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
                    desired_capabilities=webdriver.DesiredCapabilities.FIREFOX
                )
            except Exception as err:  # pylint: disable=broad-except
                # Capture the raised exception for later usage and wait
                # a few for the next attempt.
                exception = err
                time.sleep(.5)
            else:
                # Connection succeeded time to leave the for loop
                break
        else:
            # Reraise the captured exception.
            six.raise_from(
                DockerBrowserError(
                    'Failed to connect the webdriver to the containerized '
                    'selenium.'
                ),
                exception
            )

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
        """Create a docker container running a ``standalone-firefox`` selenium.

        Make sure to have the image ``selenium/standalone-firefox`` already
        pulled.
        """
        if self.container:
            return
        self.container = self._client.create_container(
            detach=True,
            environment={
                'SCREEN_WIDTH': '1920',
                'SCREEN_HEIGHT': '1080',
            },
            host_config=self._client.create_host_config(
                publish_all_ports=True),
            image='selenium/standalone-firefox',
            name=self._name.split('.')[-1] + '_{0}'.format(
                gen_string('alphanumeric', 3)),
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
         return (typeof angular === "undefined") ? true :
          angular.element(document).injector().get(
           "$http").pendingRequests.length < 1
        }
        function spinnerInvisible() {
         spinner = document.getElementById("turbolinks-progress")
         return (spinner === null) ? true : spinner.style["display"] == "none"
        }
        return {
            jquery: jqueryInactive(),
            ajax: ajaxInactive(),
            angular: angularNoRequests(),
            spinner: spinnerInvisible(),
            document: document.readyState == "complete",
        }
        '''

    def before_click(self, element):
        """Invoked before clicking on an element. Ensure page is fully loaded
        before clicking.
        """
        self.ensure_page_safe()

    def after_click(self, element):
        """Invoked after clicking on an element. Ensure page is fully loaded
        before proceeding further.
        """
        self.ensure_page_safe()


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
