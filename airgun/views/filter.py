from widgetastic.widget import (
    Table,
    Text,
    TextInput,
)
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Pagination as PF4Pagination

from airgun.views.common import BaseLoggedInView
from airgun.widgets import (
    ActionsDropdown,
    PF4FilteredDropdown,
    PF4MultiSelect,
    Search,
)


class FiltersView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    searchbox = Search()
    new = Text("//a[contains(@href, '/filters/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )
    pagination = PF4Pagination()

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
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
    filter = TextInput(id='search')
    submit = Text('//button[@data-ouia-component-id="filters-submit-button"]')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read().startswith('Edit filter for ')
        )


class FilterCreateView(FilterDetailsView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Create Filter'
        )
