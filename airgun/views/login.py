from widgetastic.widget import ClickableMixin, Text, TextInput, View


class LoginView(View, ClickableMixin):
    username = TextInput(id='login_login')
    password = TextInput(id='login_password')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.username, exception=False) is not None
