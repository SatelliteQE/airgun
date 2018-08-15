from widgetastic.widget import Text, TextInput

from airgun.views.common import BaseLoggedInView
from airgun.widgets import ActionsDropdown, SatTable


class AllRulesView(BaseLoggedInView):
    title = Text(".//h1[normalize-space(.)='Rules']")
    search = TextInput(locator=".//input[@placeholder='Search rules']")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.search.is_displayed


class InventoryAllHosts(BaseLoggedInView):
    title = Text(".//h1[normalize-space(.)='Inventory']")
    search = TextInput(locator=".//input[@placeholder='Find a system']")
    actions = ActionsDropdown(".//div[contains(@class, 'dropdown')]")
    systems_count = Text(".//h3[@class='system-count']")
    table = SatTable(".//table",
                     column_widgets={"System Name": Text(".//a")})

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.search.is_displayed


class InventoryHostDetails(BaseLoggedInView):
    hostname = Text(".//div[@class='modal-title']/h2/div/span")
    close = Text(".//div[contains(@class, 'fa-close'])")

    @property
    def is_displayed(self):
        return self.hostname.is_displayed and self.close.is_displayed
