from cached_property import cached_property
from selenium.common.exceptions import NoSuchElementException
from taretto.navigate import Navigate, NavigateStep, NavigateToSibling
from taretto.ui import Browser, DefaultPlugin

from airgun import settings
from airgun.base.browser_manager import BrowserManager
from airgun.base.application.implementations import AirgunImplementationContext, Implementation
from airgun.views.common import BaseLoggedInView, BasePage


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

    def ensure_page_safe(self, timeout='30s'):
        """Ensures page is fully loaded.
        Default timeout was 10s, this changes it to 30s.
        """
        super().ensure_page_safe(timeout)

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
    def __init__(self, selenium_browser, endpoint, extra_objects=None):
        extra_objects = extra_objects or {}
        extra_objects.update({"application": endpoint.owner, "endpoint": endpoint})
        super(AirgunBrowser, self).__init__(
            selenium_browser,
            plugin_class=AirgunBrowserPlugin,
            extra_objects=extra_objects,
        )
        self.window_handle = selenium_browser.current_window_handle
        self.logger.info(
            "Opened browser %s %s",
            selenium_browser.capabilities.get("browserName", "unknown"),
            selenium_browser.capabilities.get("version", "unknown"),
        )

    @property
    def application(self):
        return self.extra_objects["application"]

    def create_view(self, *args, **kwargs):
        return self.application.web_ui.create_view(*args, **kwargs)


class AirgunNavigateStep(NavigateStep):
    VIEW = None

    @cached_property
    def view(self):
        if self.VIEW is None:
            raise AttributeError(
                "{} does not have VIEW specified".format(type(self).__name__)
            )
        return self.create_view(self.VIEW, additional_context={"object": self.obj})

    @property
    def application(self):
        return self.obj.application

    def create_view(self, *args, **kwargs):
        return self.application.web_ui.create_view(*args, **kwargs)

    def am_i_here(self):
        try:
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False

    def check_for_badness(self, fn, _tries, nav_args, *args, **kwargs):
        go_kwargs = kwargs.copy()
        go_kwargs.update(nav_args)
        self.log_message(
            "Invoking {}, with {} and {}".format(fn.__name__, args, kwargs),
            level="debug",
        )

        try:
            return fn(*args, **kwargs)
        except Exception as e:
            self.log_message(e)
            self.go(_tries, *args, **go_kwargs)


    def go(self, _tries=3, *args, **kwargs):
        """Wrapper around :meth:`navmazing.NavigateStep.go` which returns
        instance of view after successful navigation flow.

        :return: view instance if class attribute ``VIEW`` is set or ``None``
            otherwise
        """
        super(AirgunNavigateStep, self).go(_tries=_tries, *args, **kwargs)
        view = self.view if self.VIEW is not None else None
        return view


class WebUI(Implementation):
    """UI implementation using the normal ux"""

    navigator = Navigate()
    navigate_to = navigator.navigate
    register_destination_for = navigator.register
    register_method_for = AirgunImplementationContext.external_for
    name = "WebUI"

    def __init__(self, owner):
        super(WebUI, self).__init__(owner)
        self.browser_manager = BrowserManager()

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
        view = view_class(self.widgetastic_browser, additional_context=additional_context)
        return view

    def _reset_cache(self):
        try:
            del self.widgetastic_browser
        except AttributeError:
            pass

    @cached_property
    def widgetastic_browser(self):
        """This gives us a widgetastic browser."""
        selenium_browser = self.browser_manager.ensure_open(url_key=self.application.address)
        self.browser_manager.add_cleanup(self._reset_cache)
        return AirgunBrowser(selenium_browser, self)

    def open_login_page(self):
        self.browser_manager.ensure_open(self.application.address)

    def do_login(self):
        view = self.navigate_to(self, "LoginScreen")
        view.fill({
            "username": settings.satellite.username,
            "password": settings.satellite.password,
        })
        view.login_button.click()


@WebUI.register_destination_for(WebUI)
class LoginScreen(AirgunNavigateStep):
    VIEW = BasePage

    def am_i_here(self):
        return False

    def prerequisite(self):
        pass

    def step(self):
        self.obj.open_login_page()


@WebUI.register_destination_for(WebUI)
class LoggedIn(AirgunNavigateStep):
    VIEW = BaseLoggedInView
    prerequisite = NavigateToSibling("LoginScreen")

    def step(self):
        self.obj.do_login()
