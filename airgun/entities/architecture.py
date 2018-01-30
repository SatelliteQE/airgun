from airgun.navigation import BaseNavigator, navigator
from widgetastic.widget import View, Text, TextInput

import time


class Architecture(View):

    title = Text("//h1[text()='Architectures']")
    new = Text("//a[contains(@href, '/architectures/new')]")
    search = Text("//a[contains(., '{}')]")
    navigate_locator = "//a[@id='menu_item_architectures']"

    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    # @View.nested
    # class General(View):
    #     name = TextInput('#architecture_name')

    NAVBAR_PATH = (
        '//div[contains(@class,"navbar-inner") and '
        'not(contains(@style, "display"))]')
    MENU_CONTAINER_PATH = NAVBAR_PATH + '//ul[@id="menu"]'

    def menu_click(self, tree):
        for i, el in enumerate(tree, start=1):
            locator = self.MENU_CONTAINER_PATH + el
            self.browser.wait_for_element(locator)
            self.browser.move_to_element(locator)
            time.sleep(0.5)
            if len(tree) == i:
                self.browser.wait_for_element(locator)
                self.browser.click(locator)
                time.sleep(1)

    def create_architecture(self, values):
        navigator.navigate(self, 'All')
        self.browser.wait_for_element(self.new)
        self.browser.click(self.new)
        self.fill(values)
        self.browser.click(self.submit)


@navigator.register(Architecture, 'All')
class ShowAllArchitectures(BaseNavigator):
    VIEW = Architecture

    # prerequisite = NavigateToSibling('Dashboard')

    def step(self):
        self.obj.menu_click(
            ["//a[@id='hosts_menu']", self.obj.navigate_locator])
