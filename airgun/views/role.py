from widgetastic.widget import Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import ActionsDropdown, MultiSelect, SatTable


class RolesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Roles']")
    new = Text("//a[contains(@href, '/roles/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./span/a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class RoleEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='role_name')
    description = TextInput(id='role_description')
    locations = MultiSelect(id='ms-role_location_ids')
    organizations = MultiSelect(id='ms-role_organization_ids')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read().startswith('Edit ')
        )


class RoleCreateView(RoleEditView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Create Role'
        )


class RoleCloneView(RoleCreateView):
    """Clone Role view"""
