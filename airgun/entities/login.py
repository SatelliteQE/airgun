from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.common import BaseLoggedInView
from airgun.views.login import LoginView


class LoginEntity(BaseEntity):
    def read_sat_version(self):
        view = self.navigate_to(self, "NavigateToLogin")
        return view.read()

    def login(self, values):
        view = self.navigate_to(self, "NavigateToLogin")
        view.fill(values)
        view.submit.click()

    def logout(self):
        view = BaseLoggedInView(self.browser)
        view.flash.assert_no_error()
        view.flash.dismiss()
        view.select_logout()
        view = LoginView(self.browser)
        return view.read()


@navigator.register(LoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = LoginView

    def step(self, *args, **kwargs):
        # logout() if logged_in?
        pass

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
