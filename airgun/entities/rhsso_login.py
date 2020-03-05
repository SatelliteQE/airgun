from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.rhsso_login import LoginView


class RHSSOLoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(self, 'NavigateToLogin')
        view.fill(values)
        view.submit.click()


@navigator.register(RHSSOLoginEntity)
class NavigateToLogin(NavigateStep):
    VIEW = LoginView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
