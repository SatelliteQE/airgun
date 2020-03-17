from widgetastic.widget import ClickableMixin
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View


class RhssoLoginView(View, ClickableMixin):
    username = TextInput(id='username')
    password = TextInput(id='password')
    submit = Text('//input[@name="login"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.username, exception=False) is not None


class RhssoExtLogoutView(View, ClickableMixin):
    login_again = Text('//a[@href="/users/extlogin"]')
    logo = Text('//a[@alt="logo')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.login_again, exception=False) is not None
