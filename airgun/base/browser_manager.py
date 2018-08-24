from selenium.common.exceptions import UnexpectedAlertPresentException

from airgun.browser import SeleniumBrowserFactory


class BrowserManager(object):
    def __init__(self, provider=None, browser=None, test_name=None):
        self.factory = SeleniumBrowserFactory(provider, browser, test_name)
        self.browser = None

    def coerce_url_key(self, key):
        return key

    def _is_alive(self):
        try:
            self.browser.current_url
        except UnexpectedAlertPresentException:
            # We shouldn't think that an Unexpected alert means the browser is dead
            return True
        except Exception:
            return False
        return True

    def ensure_open(self, url_key=None):
        url_key = self.coerce_url_key(url_key)
        if getattr(self.browser, "url_key", None) != url_key:
            return self.start(url_key=url_key)

        if self._is_alive():
            return self.browser
        else:
            return self.start(url_key=url_key)

    def add_cleanup(self, callback):
        assert self.browser is not None
        try:
            cl = self.browser.__cleanup
        except AttributeError:
            cl = self.browser.__cleanup = []
        cl.append(callback)

    def _consume_cleanups(self):
        try:
            cl = self.browser.__cleanup
        except AttributeError:
            pass
        else:
            while cl:
                cl.pop()()

    def quit(self):
        self._consume_cleanups()
        try:
            self.factory.close(self.browser)
        except Exception as e:
            pass
        finally:
            self.browser = None

    def start(self, url_key=None):
        url_key = self.coerce_url_key(url_key)
        if self.browser is not None:
            self.quit()
        return self.open_fresh(url_key=url_key)

    def open_fresh(self, url_key=None):
        url_key = self.coerce_url_key(url_key)
        assert self.browser is None

        self.browser = self.factory.create(url_key=url_key)
        return self.browser
