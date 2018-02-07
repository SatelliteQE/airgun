"""Tools to help getting a browser instance to run UI tests."""
import logging
import six
import time
from copy import copy

from fauxfactory import gen_string
from selenium import webdriver
from widgetastic.browser import Browser, DefaultPlugin

from airgun import settings

try:
    import docker
except ImportError:
    # Let if fail later if not installed
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
    """Get sauce ondemand URL for a given user and key."""
    return 'http://{0}:{1}@ondemand.saucelabs.com:80/wd/hub'.format(
        saucelabs_user, saucelabs_key)


class AirgunBrowserPlugin(DefaultPlugin):
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


class SeleniumBrowserFactory(object):
    """

    Usage:
        # init factory
        factory = SeleniumBrowserFactory(test_name=test_name)
        # get factory browser
        selenium_browser = factory.get_browser()
        # navigate to desired url
        # ...
        # perform post-init hacks (e.g. skipping certificate error screen)
        factory.post_init()
        # perform your test steps
        # ...
        # perform factory clean-up
        factory.finalize(passed)

    """

    def __init__(self, browser_name=None, webdriver_name=None, test_name=None):
        self.browser = browser_name or settings.selenium.browser or 'selenium'
        self.webdriver = (
            webdriver_name or settings.selenium.webdriver or 'chrome')
        self.test_name = test_name
        self._docker = None
        self._webdriver = None

    def get_browser(self):
        if self.browser == 'selenium':
            return self.get_selenium_browser()
        elif self.browser == 'saucelabs':
            return self.get_saucelabs_browser()
        elif self.browser == 'docker':
            return self.get_docker_browser()
        else:
            raise ValueError(
                '"{}" browser is not supported. Please use one of {}'
                .format(self.browser, ('selenium', 'saucelabs', 'docker'))
            )

    def post_init(self):
        # Workaround 'Certificate Error' screen on Microsoft Edge
        if (
                self.webdriver == 'edge' and
                'Certificate Error' in self._webdriver.title or
                'Login' not in self._webdriver.title):
            self._webdriver.get(
                "javascript:document.getElementById('invalidcert_continue')"
                ".click()"
            )

    def finalize(self, passed=True):
        self._webdriver.quit()
        if self.browser == 'selenium':
            return
        elif self.browser == 'saucelabs':
            return self.finalize_saucelabs_browser(passed)
        elif self.browser == 'docker':
            return self.finalize_docker_browser()

    def get_selenium_browser(self):
        kwargs = {}
        binary = settings.selenium.webdriver_binary

        if self.webdriver == 'chrome':
            if binary:
                kwargs.update({'executable_path': binary})
            self._webdriver = webdriver.Chrome(**kwargs)
        elif self.webdriver == 'firefox':
            if binary:
                kwargs.update({
                    'firefox_binary': (
                        webdriver.firefox.firefox_binary.FirefoxBinary(binary))
                })
            self._webdriver = webdriver.Firefox(**kwargs)
        elif self.webdriver == 'ie':
            if binary:
                kwargs.update({'executable_path': binary})
            self._webdriver = webdriver.Ie(**kwargs)
        elif self.webdriver == 'edge':
            if binary:
                kwargs.update({'executable_path': binary})
            capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['javascriptEnabled'] = True
            kwargs.update({'capabilities': capabilities})
            self._webdriver = webdriver.Edge(**kwargs)
        elif self.webdriver == 'phantomjs':
            self._webdriver = webdriver.PhantomJS(
                service_args=['--ignore-ssl-errors=true'])
        elif self.webdriver == 'remote':
            self._webdriver = webdriver.Remote()
        if self._webdriver is None:
            raise ValueError(
                '"{}" webdriver is not supported. Please use one of {}'
                .format(
                    self.browser,
                    ('chrome', 'firefox', 'ie', 'edge', 'phantomjs', 'remote')
                )
            )
        return self._webdriver

    def get_saucelabs_browser(self):
        if self.webdriver == 'chrome':
            desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
            if settings.selenium.webdriver_desired_capabilities:
                desired_capabilities.update(
                    settings.selenium.webdriver_desired_capabilities)
        elif self.webdriver == 'firefox':
            desired_capabilities = webdriver.DesiredCapabilities.FIREFOX.copy()
            if settings.selenium.webdriver_desired_capabilities:
                desired_capabilities.update(
                    settings.selenium.webdriver_desired_capabilities)
        elif self.webdriver == 'ie':
            desired_capabilities = (
                webdriver.DesiredCapabilities.INTERNETEXPLORER.copy())
            if settings.selenium.webdriver_desired_capabilities:
                desired_capabilities.update(
                    settings.selenium.webdriver_desired_capabilities)
        elif self.webdriver == 'edge':
            desired_capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            desired_capabilities['acceptSslCerts'] = True
            desired_capabilities['javascriptEnabled'] = True
            if settings.selenium.webdriver_desired_capabilities:
                desired_capabilities.update(
                    settings.selenium.webdriver_desired_capabilities)
        else:
            raise ValueError(
                '"{}" webdriver on saucelabs is currently not supported. '
                'Please use one of {}'
                .format(self.browser, ('chrome', 'firefox', 'ie', 'edge'))
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

    def finalize_saucelabs_browser(self, passed):
        """SauceLabs has no way to determine whether test passed or failed
        automatically, so we explicitly 'tell' it

        :param bool passed: Whether test passed or not
        """
        sc = sauceclient.SauceClient(
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
        sc.jobs.update_job(self._webdriver.session_id, **kwargs)

    def get_docker_browser(self):
        kwargs = {}
        if self.test_name:
            kwargs.update({'name': self.test_name})
        self._docker = DockerBrowser(**kwargs)
        self._docker.start()
        self._webdriver = self._docker.webdriver
        return self._webdriver

    def finalize_docker_browser(self):
        self._docker.stop()


class DockerBrowser(object):
    """Provide a browser instance running inside a docker container."""
    def __init__(self, name=None):
        if docker is None:
            raise DockerBrowserError(
                'Package docker-py is not installed. Install it in order to '
                'use DockerBrowser.'
            )
        self.webdriver = None
        self.container = None
        self._client = None
        self._name = name
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
        for attempt in range(20):
            try:
                self.webdriver = webdriver.Remote(
                    command_executor='http://127.0.0.1:{0}/wd/hub'.format(
                        self.container['HostPort']),
                    desired_capabilities=webdriver.DesiredCapabilities.FIREFOX
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
            six.raise_from(
                DockerBrowserError(
                    'Failed to connect the webdriver to the containerized '
                    'selenium.'
                ),
                exception
            )

    def _quit_webdriver(self):
        """Quit the selenium Remote webdriver."""
        if not self.webdriver:
            return
        self.webdriver.quit()

    def _init_client(self):
        """Init docker Client.

        Make sure that docker service to be published under the
        unix://var/run/docker.sock unix socket.

        Use auto for version in order to allow docker client to
        automatically figure out the server version.
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
        """Create a docker container running a standalone-firefox
        selenium.

        Make sure to have the image selenium/standalone-firefox already
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
            name=self._name.split('.', 4)[-1] + '_{0}'.format(
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
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()


class AirgunBrowser(Browser):

    def __init__(self, selenium, session, extra_objects=None):
        extra_objects = extra_objects or {}
        extra_objects.update({
            'session': session,
        })
        super(AirgunBrowser, self).__init__(
            selenium,
            plugin_class=AirgunBrowserPlugin,
            extra_objects=extra_objects)
        self.window_handle = selenium.current_window_handle

    def create_view(self, view_class, o=None, override=None,
                    additional_context=None):
        o = o or self
        if override is not None:
            new_obj = copy(o)
            new_obj.__dict__.update(override)
        else:
            new_obj = o
        return view_class(self.browser, additional_context={'object': new_obj})
