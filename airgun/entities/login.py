from widgetastic.widget import ClickableMixin, Text, TextInput, View


class Login(View, ClickableMixin):
    username = TextInput(locator='//input[@id="login_login"]')
    password = TextInput(locator='//input[@id="login_password"]')
    submit = Text('//input[@name="commit"]')

    def login(self, values):
        self.fill(values)
        self.browser.click(self.submit)

    def logout(self):
        pass
