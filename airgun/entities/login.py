from airgun.entities.base import BaseEntity
from airgun.views.login import LoginView


class LoginEntity(BaseEntity):

    def login(self, values):
        view = self.navigate_to(LoginView, 'NavigateToLogin')
        view.fill(values)
        self.browser.click(view.submit)

    def logout(self):
        # fixme: not implemented
        pass
