"""Tools to help getting a browser instance to run UI tests."""
import logging

from selenium import webdriver

from airgun import settings

try:
    import docker
except ImportError:
    # Let if fail later if not installed
    docker = None


LOGGER = logging.getLogger(__name__)


class DockerBrowserError(Exception):
    """Indicates any issue with DockerBrowser."""


def _sauce_ondemand_url(saucelabs_user, saucelabs_key):
    """Get sauce ondemand URL for a given user and key."""
    return 'http://{0}:{1}@ondemand.saucelabs.com:80/wd/hub'.format(
        saucelabs_user, saucelabs_key)


def browser(browser_name=None, webdriver_name=None):
    """Creates a webdriver browser.

    :param browser_name: one of selenium, saucelabs, docker
    :param webdriver_name: one of firefox, chrome, edge, ie, phantomjs

    If any of the params are None then will be read from properties file.
    """

    webdriver_name = (webdriver_name or settings.selenium.webdriver).lower()
    browser_name = (browser_name or settings.selenium.browser).lower()

    if browser_name == 'selenium':
        if webdriver_name == 'firefox':
            return webdriver.Firefox()
        elif webdriver_name == 'chrome':
            return (
                webdriver.Chrome() if (
                        settings.selenium.webdriver_binary is None)
                else webdriver.Chrome(
                    executable_path=settings.selenium.webdriver_binary)
            )
        elif webdriver_name == 'ie':
            return (
                webdriver.Ie() if settings.selenium.webdriver_binary is None
                else webdriver.Ie(
                    executable_path=settings.selenium.webdriver_binary)
            )
        elif webdriver_name == 'edge':
            capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['javascriptEnabled'] = True
            return (
                webdriver.Edge(capabilities=capabilities)
                if settings.selenium.webdriver_binary is None
                else webdriver.Edge(
                    capabilities=capabilities,
                    executable_path=settings.selenium.webdriver_binary,
                )
            )
        elif webdriver_name == 'phantomjs':
            return webdriver.PhantomJS(
                service_args=['--ignore-ssl-errors=true'])
        elif webdriver_name == 'remote':
            return webdriver.Remote()
    elif browser_name == 'saucelabs':
        raise NotImplementedError
    elif browser_name == 'docker':
        raise NotImplementedError
    else:
        raise NotImplementedError(
            "Supported browsers are: selenium, saucelabs, docker"
        )
