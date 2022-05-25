from widgetastic.widget import ClickableMixin
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View


class LoginView(View, ClickableMixin):
    username = TextInput(id="login_login")
    password = TextInput(id="login_password")
    login_text = Text('//*[@id="login-footer-text"]')
    logo = Text('//img[@alt="logo"]')
    submit = Text('//button[@type="submit"]')
    version = Text('//*[@id="version"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.username, exception=False) is not None
