
from widgetastic.widget import (
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
)
from airgun.widgets import Search, SatTableWithUnevenStructure


class CustomSearch(Search):
    search_field = TextInput(locator=".//input[@role='combobox']")
    search_button = Button('Search')


class ModuleStreamView(BaseLoggedInView):
    """Main Module_Streams view"""
    title = Text("//h2[contains(., 'Module Streams')]")
    table = SatTable('.//table', column_widgets={'Name': Text("./a")})

    search_box = CustomSearch()

    def search(self, query):
        """Perform search using search box on the page and return table
        contents.

        :param str query: search query to type into search field. E.g.
            ``name = "bar"``.
        :return: list of dicts representing table rows
        :rtype: list
        """
        self.search_box.search(query)
        return self.table.read()

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ModuleStreamsDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    title = Text("//a(., 'Module Streams')]")
    details_tab = Text("//a[@id='module-stream-tabs-container-tab-1']")

    @property
    def is_displayed(self):
        """The view is displayed when it's details ta exists"""
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)

        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Module Streams'
        )

    @View.nested
    class details(SatTab):
        details_table = SatTableWithUnevenStructure(
            locator='.//table',
            column_locator='./*')

    @View.nested
    class repositories(SatTab):
        table = SatTable(
            locator=".//table",
            column_widgets={
                'Name': Text("./a"),
            }
        )
