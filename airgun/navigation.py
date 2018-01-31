from navmazing import Navigate, NavigateStep
from selenium.common.exceptions import NoSuchElementException


class BaseNavigator(NavigateStep):
    """Quickly navigate through menus and tabs."""

    VIEW = None

    @property
    def view(self):
        if self.VIEW is None:
            raise AttributeError(
                '{} does not have VIEW specified'.format(type(self).__name__)
            )
        return self.obj

    def am_i_here(self, *args, **kwargs):
        try:
            return self.view.is_displayed
        except (AttributeError, NoSuchElementException):
            return False


navigator = Navigate()
