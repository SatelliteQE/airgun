from widgetastic.widget import Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import (
    FilteredDropdown,
    ActionsDropdown,
    SatTable,
    MultiSelect,
)


class ComputeProfilesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compute Profiles']")
    new = Text("//a[contains(@href, '/compute_profiles/new')]")
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


class ComputeProfileCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(locator=".//input[@id='compute_profile_name']")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Profiles'
            and self.breadcrumb.read() == 'Create Compute Profile'
        )


class ComputeProfileDetailView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    flavor = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_flavor_id')
    availability_zone = FilteredDropdown(
        id='s2id_compute_attribute_vm_attrs_availability_zone')
    subnet = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_subnet_id')
    security_groups = MultiSelect(
        id='ms-compute_attribute_vm_attrs_security_group_ids')
    managed_ip = FilteredDropdown(
        id='s2id_compute_attribute_vm_attrs_managed_ip')
    submit = Text('//input[@name="commit"]')
    table = SatTable(
        './/table',
        column_widgets={
            'Compute Resource': Text('./a'),
        }
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Profiles'
        )


class ComputeProfileRenameView(ComputeProfileCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute profiles'
            and self.breadcrumb.read() == 'Edit Compute profile'
        )
