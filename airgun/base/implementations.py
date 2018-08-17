from airgun.navigation import navigator
from airgun.browser import SeleniumBrowserFactory


class ViaUI(object):
    """UI implementation using the normal ux"""

    navigator = navigator

    def __init__(self, owner):
        self.owner = owner
        self.manager = SeleniumBrowserFactory().get_browser()

    @property
    def application(self):
        return self.owner

    def __str__(self):
        return 'ViaUI'

    def open_browser(self, url_key=None):
        # TODO: self.application.server.address() instead of None
        return manager.ensure_open(url_key)

    def quit_browser(self):
        manager.quit()
        try:
            del self.widgetastic
        except AttributeError:
            pass

    def _reset_cache(self):
        try:
            del self.widgetastic
        except AttributeError:
            pass

    def create_view(self, view_class, additional_context=None):
        """Method that is used to instantiate a Widgetastic View.
        Views may define ``LOCATION`` on them, that implies a :py:meth:`force_navigate` call with
        ``LOCATION`` as parameter.
        Args:
            view_class: A view class, subclass of ``widgetastic.widget.View``
            additional_context: Additional informations passed to the view (user name, VM name, ...)
                which is also passed to the :py:meth:`force_navigate` in case when navigation is
                requested.
        Returns:
            An instance of the ``view_class``
        """
        additional_context = additional_context or {}
        view = view_class(
            self.widgetastic,
            additional_context=additional_context,
            logger=logger)
        return view

    @cached_property
    def widgetastic(self):
        """This gives us a widgetastic browser."""
        browser = self.open_browser(url_key=self.application.server.address())
        wt = AirgunBrowser(browser, self)
        return wt