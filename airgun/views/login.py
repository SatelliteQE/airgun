from widgetastic.widget import ClickableMixin, Text, TextInput, View


class LoginView(View, ClickableMixin):
    username = TextInput(id="login_login")
    password = TextInput(id="login_password")
    login_text = Text(".//footer[contains(@class,'login-pf-page-footer')]")
    logo = Text('//img[@alt="logo"]')
    submit = Text('//button[@type="submit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.username, exception=False) is not None
