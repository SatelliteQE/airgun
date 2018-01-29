import time
from widgetastic.widget import View


class Navigator(View):
    """Quickly navigate through menus and tabs."""

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