from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.login import LoginView


class LoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(self, 'NavigateToLogin')
        view.fill(values)
        view.submit.click()

    def logout(self):
        pass


@navigator.register(LoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = LoginView

    def step(self, *args, **kwargs):
        # logout() if logged_in?
        pass

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
