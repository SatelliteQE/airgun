"""Tools to help getting selenium and widgetastic browser instance to run UI
tests.
"""
import base64
from contextlib import contextmanager
from datetime import datetime
import logging
import os
import time
import urllib
from urllib.parse import unquote

from box import Box
from selenium import webdriver
from wait_for import TimedOutError, wait_for
from webdriver_kaifuku import BrowserManager
from widgetastic.browser import Browser, DefaultPlugin
from widgetastic.exceptions import NoAlertPresentException, NoSuchElementException
import yaml

from airgun import settings
from airgun.widgets import ConfirmationDialog, Pf4ConfirmationDialog

LOGGER = logging.getLogger(__name__)


class SeleniumBrowserFactory:
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

        # perform post-init steps (e.g. skipping certificate error screen)
        factory.post_init()

        # perform your test steps

        # perform factory clean-up
        factory.finalize(passed)

    """

    def __init__(
        self, provider=None, browser=None, test_name=None, session_cookie=None, hostname=None
    ):
        """Initializes factory with either specified or fetched from settings
        values.

        :param str optional provider: Browser provider name. One of
            ('selenium', 'remote'). If none specified -
            :attr:`settings.selenium.browser` is used.
        :param str optional browser: Browser name. One of ('chrome', 'firefox').
        :param str optional test_name: Name of the test using this factory. It
            is useful for `saucelabs` provider to update saucelabs job name, or
            for `docker` provider to create container with meaningful name, not
            used otherwise.
        :param requests.sessions.Session optional session_cookie: session object to be used
            to bypass login
        :param str optional hostname: The hostname of a target that differs from
            settings.satellite.hostname
        """
        self.provider = provider or settings.selenium.browser
        self.browser = browser or settings.selenium.webdriver
        self.web_kaifuku = Box(yaml.safe_load(settings.webkaifuku.config))
        self.test_name = test_name
        self._session = session_cookie
        self._docker = None
        self._webdriver = None
        self._hostname = hostname or settings.satellite.hostname

    def get_browser(self):
        """Returns selenium webdriver instance of selected ``provider`` and
        ``browser``.

        :return: selenium webdriver instance
        :raises: ValueError: If wrong ``provider`` or ``browser`` specified.
        """
        if self.provider == 'selenium':
            return self._get_selenium_browser(), None
        elif self.provider == 'remote':
            return self._get_remote_browser(), self.web_kaifuku.webdriver_options.command_executor
        else:
            raise ValueError(
                f'"{self.provider}" browser is not supported. '
                f'Please use one of {("selenium", "remote")}'
            )

    def post_init(self):
        """Perform all required post-init tweaks and workarounds. Should be
        called _after_ proceeding to desired url.

        :return: None
        """
        pass

    def finalize(self, passed=True):
        """Finalize browser - close browser window, report results to saucelabs
        or close docker container if needed.

        :param bool passed: Boolean value indicating whether test passed
            or not. Is only used for ``saucelabs`` provider.
        :return: None
        """
        if self.provider in ('selenium', 'remote'):
            self._webdriver.quit()
            return

    def _set_session_cookie(self):
        """Add the session cookie (if provided) to the webdriver"""
        if self._session:
            # webdriver doesn't allow to add cookies unless we land on the target domain
            # let's navigate to its invalid page to get it loaded ASAP
            self._webdriver.get(f'https://{self._hostname}/404')
            self._webdriver.add_cookie(
                {'name': '_session_id', 'value': self._session.cookies.get_dict()['_session_id']}
            )

    def _get_selenium_browser(self):
        """Returns selenium webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.

        :raises: ValueError: If wrong ``browser`` specified.
        """
        kwargs = {}
        manager_conf = {}
        binary = settings.selenium.webdriver_binary
        browseroptions = settings.selenium.browseroptions

        if self.browser == 'chrome':
            if binary:
                kwargs.update({'executable_path': binary})
            options = webdriver.ChromeOptions()
            prefs = {'download.prompt_for_download': False}
            options.add_experimental_option("prefs", prefs)
            options.add_argument('disable-web-security')
            options.add_argument('ignore-certificate-errors')
            if browseroptions:
                for opt in browseroptions.split(';'):
                    options.add_argument(opt)
            kwargs.update({'options': options})
        elif self.browser == 'firefox':
            if binary:
                kwargs.update({'executable_path': binary})
        manager_conf.update({'webdriver': self.browser})
        manager_conf.update({'webdriver_options': kwargs})
        manager = BrowserManager.from_conf(manager_conf)
        self._webdriver = manager.start()
        if self._webdriver is None:
            raise ValueError(
                f'"{self.browser}" webdriver is not supported. '
                f'Please use one of {("chrome", "firefox")}'
            )
        self._set_session_cookie()
        return self._webdriver

    def _get_remote_browser(self):
        """Returns remote webdriver instance of selected ``browser``.

        Note: should not be called directly, use :meth:`get_browser` instead.
        """
        if self.test_name:
            self.web_kaifuku.webdriver_options.desired_capabilities.update(
                {'se:test_name': self.test_name}
            )
        manager = BrowserManager.from_conf(self.web_kaifuku)
        self._webdriver = manager.start()
        self._set_session_cookie()
        return self._webdriver


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

    def __init__(self, *args, **kwargs):
        self._ignore_ensure_page_safe_timeout = False
        super().__init__(*args, **kwargs)

    @property
    def ignore_ensure_page_safe_timeout(self):
        return self._ignore_ensure_page_safe_timeout

    @ignore_ensure_page_safe_timeout.setter
    def ignore_ensure_page_safe_timeout(self, value):
        self._ignore_ensure_page_safe_timeout = value

    def ensure_page_safe(self, timeout='30s'):
        """Ensures page is fully loaded.
        Default timeout was 10s, this changes it to 30s.
        If self.ignore_ensure_page_safe_timeout is True, the function doesn't raise an exception
        and continues as if the page was safe instead. This can be used to bypass
        some bugs, e.g. https://bugzilla.redhat.com/show_bug.cgi?id=2106022
        """
        try:
            if self.ignore_ensure_page_safe_timeout:
                # set lower timeout, otherwise the page will be stuck in a lot of waiting because
                # once broken, ensure_page_safe will always timeout until loading a new page
                timeout = '2s'  # experiments show 5s let the page load properly w/o much waiting
            super().ensure_page_safe(timeout)
        except TimedOutError:
            if not self.ignore_ensure_page_safe_timeout:
                raise

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

    def do_refresh(self):
        """
        Refresh current page.
        """

        self.browser.refresh()
        self.browser.plugin.ensure_page_safe()


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
        super().__init__(selenium, plugin_class=AirgunBrowserPlugin, extra_objects=extra_objects)
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
        script = (
            'var currentdate = new Date(); '
            'return ('
            'currentdate.getFullYear() + "-" '
            '+ (currentdate.getMonth()+1) + "-" '
            '+ currentdate.getDate() + " : " '
            '+ currentdate.getHours() + ":" '
            '+ currentdate.getMinutes()'
            ');'
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
        time.sleep(3)
        script = (
            'return downloads.Manager.get().items_'
            '.filter(e => e.state === "COMPLETE")'
            '.map(e => e.file_url || e.fileUrl);'
        )
        if self.browser_type == 'chrome':
            script = (
                'return document.querySelector("downloads-manager")'
                '.shadowRoot.querySelector("#downloadsList")'
                '.items.filter(e => e.state === "COMPLETE")'
                '.map(e => e.filePath || e.file_path || e.fileUrl || e.file_url);'
            )
        return self.execute_script(script)

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
        # In some version <= 98, this changed so schema is not included in the path
        if 'file://' in uri or 'http://' in uri:
            elem.send_keys(unquote(uri[7:]))
        else:
            elem.send_keys(unquote(uri))

        result = self.selenium.execute_async_script(
            "var input = arguments[0], callback = arguments[1]; "
            "var reader = new FileReader(); "
            "reader.onload = function (ev) { callback(reader.result) }; "
            "reader.onerror = function (ex) { callback(ex.message) }; "
            "reader.readAsDataURL(input.files[0]); "
            "input.remove(); ",
            elem,
        )

        if not result.startswith('data:'):
            raise Exception(f"Failed to get file content: {result}")
        result_index = int(result.find('base64,')) + 7
        return base64.b64decode(result[result_index:])

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
        if not save_path and settings.selenium.browser == 'selenium':
            # if test is running locally, there's no need to save the file once
            # again except when explicitly asked to
            file_path = urllib.parse.unquote(urllib.parse.urlparse(file_uri).path)
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

    def check_alert(self, locator):
        try:
            return self.move_to_element(locator).is_displayed()
        except NoSuchElementException:
            self.logger.info(f'No {locator} type alert detected !')
        return False

    def get_alert(self, squash=False):
        """Returns the current alert/PF4 alert object.

        :param bool optional squash: Whether or not to squash errors during alert handling.
                Default False
        Raises:
            :py:class:`selenium.common.exceptions.NoAlertPresentException`
        """
        pf4_modal_locator = "//div[@data-ouia-component-type='PF4/ModalContent']"
        modal_locator = "//div[@class='modal-content']"
        modal_map = {pf4_modal_locator: Pf4ConfirmationDialog, modal_locator: ConfirmationDialog}
        if not self.handles_alerts:
            return None
        try:
            return self.selenium.switch_to.alert
        except NoAlertPresentException:
            for locator, locator_class in modal_map.items():
                if self.check_alert(locator):
                    return locator_class(self.browser)
            if squash:
                return False
            else:
                raise

    def handle_alert(
        self,
        cancel=False,
        wait=30.0,
        squash=False,
        prompt=None,
        check_present=False,
    ):
        """Extend the behaviour of widgetstatic.browser.handle_alert to handle PF4 alerts"""
        popup = self.get_alert(squash=squash)
        if isinstance(popup, Pf4ConfirmationDialog | ConfirmationDialog):
            if cancel:
                self.logger.info("  dismissing")
                popup.cancel()
            else:
                self.logger.info("  accepting")
                popup.confirm()
        else:
            super(AirgunBrowser, self.browser).handle_alert(
                cancel=cancel, wait=wait, squash=squash, prompt=prompt, check_present=check_present
            )

    @contextmanager
    def ignore_ensure_page_safe_timeout(self):
        try:
            self.plugin.ignore_ensure_page_safe_timeout = True
            yield
        finally:
            self.plugin.ignore_ensure_page_safe_timeout = False
