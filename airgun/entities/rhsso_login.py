from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.common import BaseLoggedInView
from airgun.views.rhsso_login import RhssoExtLogoutView
from airgun.views.rhsso_login import RhssoLoginView


class RHSSOLoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(self, 'NavigateToLogin')
        view.fill(values)
        view.submit.click()

    def login_again(self):
        view = RhssoExtLogoutView(self.browser)
        view.login_again.click()
        return view.read()

    def logout(self):
        view = BaseLoggedInView(self.browser)
        view.taxonomies.select_logout()
        view.flash.assert_no_error()
        view.flash.dismiss()
        view = RhssoExtLogoutView(self.browser)
        return view.read()


@navigator.register(RHSSOLoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = RhssoLoginView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
