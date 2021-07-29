from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import Button

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SatTable
from airgun.widgets import SatTableWithUnevenStructure
from airgun.widgets import Search


class CustomSearch(Search):
    search_field = TextInput(id='downshift-0-input')
    search_button = Button('Search')


class AnsibleCollectionsView(BaseLoggedInView):
    """Main Ansible Collections view"""

    title = Text("//h2[contains(., 'Ansible Collections')]")
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
        return self.browser.wait_for_element(self.title, exception=False) is not None


class AnsibleCollectionsDetailsView(BaseLoggedInView):

    details_tab = Text("//a[@id='content-tabs-container-tab-1']")

    @property
    def is_displayed(self):
        """Assume the view is displayed when details tab visible"""
        tab_loaded = self.browser.wait_for_element(details_tab, exception=False)
        return tab_loaded 

    @View.nested
    class details(SatTab):
        details_table = SatTableWithUnevenStructure(locator='.//table', column_locator='./*')

    @View.nested
    class repositories(SatTab):
        table = Table(
            locator=".//table",
            column_widgets={
                'Name': Text("./a"),
            },
        )
