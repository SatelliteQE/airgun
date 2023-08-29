from widgetastic.widget import Checkbox, Table, Text
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Button, PatternflyTable

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import ActionsDropdown, Pagination


class ImportPagination(Pagination):
    PER_PAGE_BUTTON_DROPDOWN = ".//div[button[@id='pagination-options-menu-toggle-2']]"
    total_items = Text("//span[@class='pf-c-optionsmenu__toggle-text']/b[2]")


class AnsibleRolesView(BaseLoggedInView, SearchableViewMixin):
    """Main Ansible Roles view. Prior to importing any roles, only the import_button
    is present, without the search widget or table.
    """

    title = Text("//h1[contains(normalize-space(.),'Ansible Roles')]")
    import_button = Text("//a[contains(@href, '/ansible_roles/import')]")
    submit = Button('Submit')
    total_imported_roles = Text("//span[@class='pf-c-options-menu__toggle-text']//b[2]")
    table = Table(
        './/table',
        column_widgets={
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.import_button.is_displayed


class AnsibleRolesImportView(BaseLoggedInView):
    """View while selecting Ansible roles to import."""

    breadcrumb = BreadCrumb()
    total_available_roles = Text("//span[@class='pf-c-options-menu__toggle-text']/b[2]")
    select_all = Checkbox(locator="//input[@id='select-all']")
    table = PatternflyTable(
        component_id='OUIA-Generated-Table-2',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
        },
    )
    pagination = Pagination()
    submit = Button('Submit')
    cancel = Button('Cancel')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Changed Ansible roles'
        )
