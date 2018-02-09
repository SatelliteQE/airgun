from cached_property import cached_property
import navmazing
from selenium.common.exceptions import NoSuchElementException


class BaseNavigator(navmazing.NavigateStep):
    """Quickly navigate through menus and tabs."""

    VIEW = None

    @cached_property
    def view(self):
        if self.VIEW is None:
            raise AttributeError(
                '{} does not have VIEW specified'.format(type(self).__name__))
        return self.create_view(self.VIEW,
                                additional_context={'object': self.obj})

    def create_view(self, *args, **kwargs):
        return self.navigate_obj.browser.create_view(*args, **kwargs)

    def am_i_here(self, *args, **kwargs):
        try:
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False

    def go(self, _tries=0, *args, **kwargs):
        super(BaseNavigator, self).go(_tries=_tries, *args, **kwargs)
        view = self.view if self.VIEW is not None else None
        return view


class Navigate(navmazing.Navigate):

    def __init__(self, browser=None):
        super(Navigate, self).__init__()
        self.browser = browser


navigator = Navigate()
