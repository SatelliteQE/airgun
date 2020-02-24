from widgetastic.widget import Checkbox
from widgetastic.widget import ConditionalSwitchableView
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.widgets import ActionsDropdown
from airgun.widgets import FilteredDropdown
from airgun.widgets import MultiSelect
from airgun.widgets import SatTable
from airgun.widgets import Search


class FiltersView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    searchbox = Search()
    new = Text("//a[contains(@href, '/filters/new')]")
    table = SatTable(
        ".//table",
        column_widgets={
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Roles'
                and self.breadcrumb.read().endswith(' filters')
        )

    def search(self, query):
        value = self.searchbox.read()
        role_id = [int(s) for s in value.split() if s.isdigit()]
        if len(role_id) > 0:
            query = 'role_id = {} and resource = "{}"'.format(
                role_id[0], query)
        self.searchbox.search(query)
        return self.table.read()


class FilterDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    resource_type = FilteredDropdown(id='filter_resource_type')
    permission = MultiSelect(id='ms-filter_permission_ids')
    override = Checkbox(id='override_taxonomy_checkbox')
    unlimited = Checkbox(id='filter_unlimited')
    filter = TextInput(id='search')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Roles'
                and self.breadcrumb.read().startswith('Edit filter for ')
        )

    taxonomies_tabs = ConditionalSwitchableView(reference='override')

    @taxonomies_tabs.register(True)
    class Taxonomies(View):
        @View.nested
        class locations(SatTab):
            resources = MultiSelect(id='ms-filter_location_ids')

        @View.nested
        class organizations(SatTab):
            resources = MultiSelect(id='ms-filter_organization_ids')

    @taxonomies_tabs.register(False)
    class NoTaxonomies(View):
        pass


class FilterCreateView(FilterDetailsView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Roles'
                and self.breadcrumb.read() == 'Create Filter'
        )
