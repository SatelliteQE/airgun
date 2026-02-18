from widgetastic.widget import ClickableMixin, Text, TextInput, View


class LoginView(View, ClickableMixin):
    username = TextInput(id='login_login')
    password = TextInput(id='login_password')
    login_text = Text(".//footer[contains(@class,'pf-v5-c-login__footer')]")
    logo = Text('//img[@class="pf-v5-c-brand"]')
    submit = Text('//button[@type="submit"]')

    @property
    def is_displayed(self):
        return self.username.is_displayed
