from widgetastic.widget import ClickableMixin, Text, TextInput, View


class RhssoLoginView(View, ClickableMixin):
    username = TextInput(id='username')
    password = TextInput(id='password')
    submit = Text('//input[@name="login"]')
    error_message = Text('//span[@id="input-error"]')

    @property
    def is_displayed(self):
        return self.username.is_displayed


class RhssoExternalLogoutView(View, ClickableMixin):
    login_again = Text('//a[@href="/users/extlogin"]')
    logo = Text('//img[@alt="logo"]')

    @property
    def is_displayed(self):
        return self.login_again.is_displayed


class RhssoTwoFactorSuccessView(View, ClickableMixin):
    code = TextInput(id='code')

    @property
    def is_displayed(self):
        return self.code.is_displayed


class RhssoTotpView(View, ClickableMixin):
    totp = TextInput(id='otp')
    submit = Text('//input[@name="login"]')

    @property
    def is_displayed(self):
        return self.totp.is_displayed
