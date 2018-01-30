"""Tools to help getting a browser instance to run UI tests."""
# fixme: 99% of copypasted from robottelo code
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


# Dict of callables to format the output of selenium commands logging
param_formatters = {
    # normally this value is ['a', 'b', 'c'] but we want ['abc']
    'sendKeysToElement': lambda x: {
        'id': x['id'], 'value': ''.join(x['value'])
    }
}


class DriverLoggerMixin(object):
    """Custom Driver Mixin to allow logging of commands execution"""
    def execute(self, driver_command, params=None):
        # execute and intercept the response
        response = super(DriverLoggerMixin, self).execute(driver_command,
                                                          params)

        # skip messages for commands not in settings
        if driver_command not in settings.selenium.log_driver_commands:
            return response

        if params:
            # we dont need the sessionId in the log output
            params.pop('sessionId', None)
            value = response.get('value')
            id_msg = ''
            # append the 'id' of element in the front of message
            if isinstance(value, webdriver.remote.webelement.WebElement):
                id_msg = "id: %s" % value.id
            # Build the message like 'findElement: id: 1: {using: xpath}'
            msg = '%s: %s %s' % (
                driver_command,
                id_msg,
                param_formatters.get(driver_command, lambda x: x)(params)
            )
        else:
            msg = driver_command

        # output the log message
        LOGGER.debug(msg)

        return response


class Firefox(DriverLoggerMixin, webdriver.Firefox):
    """Custom Firefox for custom logging"""


class Chrome(DriverLoggerMixin, webdriver.Chrome):
    """Custom Chrome for custom logging"""


class Edge(DriverLoggerMixin, webdriver.Edge):
    """Custom Edge for custom logging"""


class Ie(DriverLoggerMixin, webdriver.Ie):
    """Custom Ie for custom logging"""


class PhantomJS(DriverLoggerMixin, webdriver.PhantomJS):
    """Custom PhantomJS for custom logging"""


class Remote(DriverLoggerMixin, webdriver.Remote):
    """Custom Remote for custom logging"""


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
            return Firefox()
        elif webdriver_name == 'chrome':
            return (
                Chrome() if settings.selenium.webdriver_binary is None
                else Chrome(
                    executable_path=settings.selenium.webdriver_binary)
            )
        elif webdriver_name == 'ie':
            return (
                Ie() if settings.selenium.webdriver_binary is None
                else Ie(executable_path=settings.selenium.webdriver_binary)
            )
        elif webdriver_name == 'edge':
            capabilities = webdriver.DesiredCapabilities.EDGE.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['javascriptEnabled'] = True
            return (
                Edge(capabilities=capabilities)
                if settings.selenium.webdriver_binary is None
                else Edge(
                    capabilities=capabilities,
                    executable_path=settings.selenium.webdriver_binary,
                )
            )
        elif webdriver_name == 'phantomjs':
            return PhantomJS(
                service_args=['--ignore-ssl-errors=true'])
        elif webdriver_name == 'remote':
            return Remote()
    elif browser_name == 'saucelabs':
        raise NotImplementedError
    elif browser_name == 'docker':
        raise NotImplementedError
    else:
        raise NotImplementedError(
            "Supported browsers are: selenium, saucelabs, docker"
        )
