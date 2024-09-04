from widgetastic.widget import ClickableMixin, Text, TextInput, View


class RhssoLoginView(View, ClickableMixin):
    username = TextInput(id='username')
    password = TextInput(id='password')
    submit = Text('//input[@name="login"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.username, exception=False) is not None


class RhssoExternalLogoutView(View, ClickableMixin):
    login_again = Text('//a[@href="/users/extlogin"]')
    logo = Text('//img[@alt="logo"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.login_again, exception=False) is not None


class RhssoTwoFactorSuccessView(View, ClickableMixin):
    code = TextInput(id='code')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.code, exception=False) is not None


class RhssoTotpView(View, ClickableMixin):
    totp = TextInput(id='otp')
    submit = Text('//input[@name="login"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.totp, exception=False) is not None
