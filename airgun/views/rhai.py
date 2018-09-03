from widgetastic.widget import Table, Text, TextInput
from widgetastic_patternfly import Button

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


class OverviewDetailsView(BaseLoggedInView):
    title = Text(".//h1[normalize-space(.)='Overview']")
    inventory = Table(".//section[contains(., 'Newest Systems')]//table")
    security_issues = Text(".//div[@ng-if='securityErrors']/div")
    stability_issues = Text(".//div[@ng-if='stabilityErrors']/div")
    inventory_link = Text(".//span[normalize-space(.)='View inventory']")
    actions_link = Text(".//span[normalize-space(.)='View actions']")

    @property
    def is_displayed(self):
        return (
            self.title.is_displayed and
            self.inventory_link.is_displayed and
            self.actions_link.is_displayed
        )


class ActionsDetailsView(BaseLoggedInView):
    title = Text(".//h1[normalize-space(.)='Actions']")
    export_csv = Button("Export CSV")
    stability_issues = Text(".//a[@class='stability']/span[@class='count']")
    security_issues = Text(".//a[@class='security']/span[@class='count']")

    @property
    def is_displayed(self):
        return self.title.is_displayed
