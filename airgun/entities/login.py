from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView
from airgun.views.login import LoginView


class LoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(self, 'NavigateToLogin')
        view.fill(values)
        view.submit.click()

    def logout(self):
        view = BaseLoggedInView(self.browser)
        view.taxonomies.select_logout()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(LoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = LoginView

    def step(self, *args, **kwargs):
        # logout() if logged_in?
        pass

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
