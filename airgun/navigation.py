from navmazing import Navigate, NavigateStep
from selenium.common.exceptions import NoSuchElementException


class BaseNavigator(NavigateStep):
    """Quickly navigate through menus and tabs."""

    VIEW = None

    def am_i_here(self, *args, **kwargs):
        try:
            return self.obj.is_displayed
        except (AttributeError, NoSuchElementException):
            return False


navigator = Navigate()
