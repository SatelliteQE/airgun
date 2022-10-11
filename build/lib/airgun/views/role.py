from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown
from airgun.widgets import MultiSelect
from airgun.widgets import SatTable


class RolesView(BaseLoggedInView, SearchableViewMixin):
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
        return self.browser.wait_for_element(self.title, exception=False) is not None


class RoleEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='role_name')
    description = TextInput(id='role_description')
    locations = MultiSelect(id='ms-role_location_ids')
    organizations = MultiSelect(id='ms-role_organization_ids')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read().startswith('Edit ')
        )


class RoleCreateView(RoleEditView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Roles'
            and self.breadcrumb.read() == 'Create Role'
        )


class RoleCloneView(RoleCreateView):
    """Clone Role view"""
