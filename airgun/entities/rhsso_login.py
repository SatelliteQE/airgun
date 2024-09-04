from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView
from airgun.views.rhsso_login import (
    RhssoExternalLogoutView,
    RhssoLoginView,
    RhssoTotpView,
    RhssoTwoFactorSuccessView,
)


class RHSSOLoginEntity(BaseEntity):
    def login(self, values, external_login=False, totp=None):
        if external_login:
            view = RhssoExternalLogoutView(self.browser)
            view.login_again.click()
        else:
            view = self.navigate_to(self, 'NavigateToLogin')
            view.fill(values)
            view.submit.click()
            if totp:
                view = RhssoTotpView(self.browser)
                view.fill(totp)
                view.submit.click()

    def logout(self):
        view = BaseLoggedInView(self.browser)
        view.select_logout()
        view.flash.assert_no_error()
        view.flash.dismiss()
        view = RhssoExternalLogoutView(self.browser)
        return view.read()

    def get_two_factor_login_code(self, values, url):
        self.browser.selenium.get(url)
        self.login(values)
        view = RhssoTwoFactorSuccessView(self.browser)
        return view.read()


@navigator.register(RHSSOLoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = RhssoLoginView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
