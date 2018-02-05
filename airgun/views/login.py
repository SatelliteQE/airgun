from widgetastic.widget import ClickableMixin, Text, TextInput, View

from airgun.navigation import BaseNavigator, navigator


class LoginView(View, ClickableMixin):
    username = TextInput(locator='//input[@id="login_login"]')
    password = TextInput(locator='//input[@id="login_password"]')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.username, exception=False) is not None


@navigator.register(LoginView)
class NavigateToLogin(BaseNavigator):
    VIEW = LoginView

    def step(self, *args, **kwargs):
        # fixme: logout() if logged_in
        pass

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
