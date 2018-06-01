from widgetastic.widget import Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import ActionsDropdown, MultiSelect, SatTable


class RolesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Roles']")
    new = Text("//a[contains(@href, '/roles/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class RoleEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='role_name')
    description = TextInput(id='role_description')
    locations = MultiSelect(id='ms-role_location_ids')
    organizations = MultiSelect(id='ms-role_organization_ids')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Roles'
                and self.breadcrumb.read().starts_with('Edit ')
        )


class RoleCreateView(RoleEditView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Roles'
                and self.breadcrumb.read() == 'Create Role'
        )
