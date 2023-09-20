from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Table,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Pagination as PF4Pagination

from airgun.views.common import BaseLoggedInView, SatTab
from airgun.widgets import (
    ActionsDropdown,
    MultiSelect,
    Pagination,
    Search,
    PF4FilteredDropdown,
    PF4MultiSelect
)


class FiltersView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    searchbox = Search()
    new = Text("//a[contains(@href, '/filters/new')]")
    table = Table(
        ".//table",
        column_widgets={
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )
    pagination = PF4Pagination()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read().endswith(' filters')
        )

    def search(self, query):
        value = self.searchbox.read()
        role_id = [int(s) for s in value.split() if s.isdigit()]
        if len(role_id) > 0:
            query = f'role_id = {role_id[0]} and resource = "{query}"'
        self.searchbox.search(query)
        return self.table.read()


class FilterDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    resource_type = PF4FilteredDropdown(
        locator='.//div[@data-ouia-component-id="resource-type-select"]'
    )
    permission = PF4MultiSelect('.//div[@id="permission-duel-select"]')
    override = Checkbox(id='override_taxonomy_checkbox')
    unlimited = Checkbox(id='filter_unlimited')
    filter = TextInput(id='search')
    submit = Text('//button[@data-ouia-component-id="filters-submit-button"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Create Filter'
        )
