from widgetastic.widget import ClickableMixin
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View


class LoginView(View, ClickableMixin):
    username = TextInput(id='username')
    password = TextInput(id='password')
    submit = Text('//input[@name="login"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.username, exception=False) is not None
