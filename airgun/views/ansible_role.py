from widgetastic.widget import Checkbox, Table, Text
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly5 import (
    Button as PF5button,
    CompactPagination as PF5CompactPagination,
    Pagination as PF5Pagination,
    PatternflyTable as PF5PatternflyTable,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import ActionsDropdown


class AnsibleRolesView(BaseLoggedInView, SearchableViewMixin):
    """Main Ansible Roles view. Prior to importing any roles, only the import_button
    is present, without the search widget or table.
    """

    title = Text("//h1[contains(normalize-space(.),'Ansible Roles')]")
    import_button = Text("//a[contains(@href, '/ansible_roles/import')]")
    submit = PF5button('Submit')
    total_imported_roles = Text("//span[@class='pf-c-options-menu__toggle-text']//b[2]")
    table = Table(
        './/table',
        column_widgets={
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )
    pagination = PF5Pagination()

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.import_button.is_displayed


class AnsibleRolesImportView(BaseLoggedInView):
    """View while selecting Ansible roles to import."""

    breadcrumb = BreadCrumb()
    total_available_roles = Text("//span[@class='pf-v5-c-menu-toggle__text']/b[2]")
    select_all = Checkbox(locator="//input[@id='select-all']")
    table = PF5PatternflyTable(
        component_id='ansible-roles-and-variables-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
        },
    )
    roles = Text("//table[contains(@class, 'pf-v5-c-table')]")
    dropdown = Text("//button[contains(@class, 'pf-v5-c-menu-toggle')]")
    max_per_pg = Text("//ul[contains(@class, 'pf-v5-c-menu__list')]/li[6]")
    pagination = PF5CompactPagination()
    submit = PF5button('Submit')
    cancel = PF5button('Cancel')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Changed Ansible roles'
        )
