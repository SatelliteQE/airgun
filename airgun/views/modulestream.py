from widgetastic.widget import Table, Text, Widget

from airgun.views.common import (
    BaseLoggedInView,
    SatTable,
    SearchableViewMixinPF4,
)


class DescriptionList(Widget):
    """Widget to read a PF5 description list (dl/dt/dd) as a dictionary."""

    ROOT = './/dl'

    def read(self):
        """Read all dt/dd pairs and return as dictionary."""
        result = {}
        dt_elements = self.browser.elements('.//dt', parent=self)
        for dt in dt_elements:
            key = self.browser.text(dt).strip()
            dd = self.browser.element('./following-sibling::dd[1]', parent=dt)
            value = self.browser.text(dd).strip()
            result[key] = value
        return result


class ModuleStreamView(BaseLoggedInView, SearchableViewMixinPF4):
    """Main Module_Streams view"""

    title = Text('//h1[contains(., "Module Streams")]')
    table = SatTable(
        ".//table[@data-ouia-component-id='content-table']",
        column_widgets={'Name': Text('./a')},
    )

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ModuleStreamsDetailsView(BaseLoggedInView):
    title = Text("//h2[contains(@class, 'pf-v5-c-title')]")
    details_tab = Text("//button[normalize-space(.)='Details']")

    @property
    def is_displayed(self):
        """Check if details page is displayed by looking for the Details tab"""
        return self.browser.wait_for_element(self.details_tab, exception=False) is not None

    details_table = DescriptionList()

    repositories_tab = Text(".//button[normalize-space(.)='Repositories']")
    profiles_tab = Text(".//button[normalize-space(.)='Profiles']")
    artifacts_tab = Text(".//button[normalize-space(.)='Artifacts']")

    repositories_table = Table(
        locator=".//table[@data-ouia-component-id='content-table']",
        column_widgets={'Name': Text('./a')},
    )
    profiles_table = SatTable(".//table[@data-ouia-component-id='content-table']")
    artifacts_table = SatTable(".//table[@data-ouia-component-id='content-table']")
