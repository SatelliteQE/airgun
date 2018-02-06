from airgun.entities.base import BaseEntity
from airgun.navigation import BaseNavigator, navigator
from airgun.views.login import LoginView


class LoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(self, 'NavigateToLogin')
        view.fill(values)
        self.browser.click(view.submit)

    def logout(self):
        # fixme: not implemented
        pass


@navigator.register(LoginEntity)
class NavigateToLogin(BaseNavigator):
    VIEW = LoginView

    def step(self, *args, **kwargs):
        # fixme: logout() if logged_in
        pass

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
