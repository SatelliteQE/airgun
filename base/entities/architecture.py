from base.navigation import Navigator
from widgetastic.widget import View, Text, TextInput


class Architecture(View):

    navigator = Navigator()
    new = Text("//a[contains(@href, '/architectures/new')]")
    search = Text("//a[contains(., '{}')]")
    navigate_locator = "//a[@id='menu_item_architectures']"

    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')

    # @View.nested
    # class General(View):
    #     name = TextInput('#architecture_name')

    def navigate(self):
        self.navigator.menu_click(["//a[@id='hosts_menu']", self.navigate_locator])

    def create_architecture(self, values):
        self.navigate()
        self.browser.wait_for_element(self.new)
        self.browser.click(self.new)
        self.fill(values)
        self.browser.click(self.submit)