from widgetastic.widget import Checkbox, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatVerticalTab, SearchableViewMixin
from airgun.widgets import (
    ActionsDropdown,
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
)


class LocationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Locations']")
    new = Text("//a[contains(@href, '/locations/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class LocationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    parent_location = FilteredDropdown(id='location_parent_id')
    name = TextInput(id='location_name')
    description = TextInput(id='location_description')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Locations'
            and self.breadcrumb.read() == 'New Location'
        )


class LocationsEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text("//form[contains(@id, 'edit')]//input[@name='commit']")
    cancel = Text("//a[normalize-space(.)='Cancel']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Locations'
            and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class primary(SatVerticalTab):
        parent_location = FilteredDropdown(id='location_parent_id')
        name = TextInput(id='location_name')
        description = TextInput(id='location_description')

    @View.nested
    class users(SatVerticalTab):
        all_users = Checkbox(id='location_ignore_types_user')
        resources = MultiSelect(id='ms-location_user_ids')

    @View.nested
    class capsules(SatVerticalTab):
        all_capsules = Checkbox(id='location_ignore_types_smartproxy')
        resources = MultiSelect(id='ms-location_smart_proxy_ids')

    @View.nested
    class subnets(SatVerticalTab):
        all_subnets = Checkbox(id='location_ignore_types_subnet')
        resources = MultiSelect(id='ms-location_subnet_ids')

    @View.nested
    class compute_resources(SatVerticalTab):
        TAB_NAME = 'Compute Resources'
        all_resources = Checkbox(id='location_ignore_types_computeresource')
        resources = MultiSelect(id='ms-location_compute_resource_ids')

    @View.nested
    class media(SatVerticalTab):
        all_medias = Checkbox(id='location_ignore_types_medium')
        resources = MultiSelect(id='ms-location_medium_ids')

    @View.nested
    class provisioning_templates(SatVerticalTab):
        TAB_NAME = 'Provisioning Templates'
        all_templates = Checkbox(id='location_ignore_types_provisioningtemplate')
        resources = MultiSelect(id='ms-location_provisioning_template_ids')

    @View.nested
    class partition_tables(SatVerticalTab):
        TAB_NAME = 'Partition Tables'
        all_ptables = Checkbox(id='location_ignore_types_ptable')
        resources = MultiSelect(id='ms-location_ptable_ids')

    @View.nested
    class domains(SatVerticalTab):
        all_domains = Checkbox(id='location_ignore_types_domain')
        resources = MultiSelect(id='ms-location_domain_ids')

    @View.nested
    class realms(SatVerticalTab):
        all_realms = Checkbox(id='location_ignore_types_realm')
        resources = MultiSelect(id='ms-location_realm_ids')

    @View.nested
    class environments(SatVerticalTab):
        all_environments = Checkbox(id='location_ignore_types_environment')
        resources = MultiSelect(id='ms-location_environment_ids')

    @View.nested
    class host_groups(SatVerticalTab):
        TAB_NAME = 'Host Groups'
        all_hostgroups = Checkbox(id='location_ignore_types_hostgroup')
        resources = MultiSelect(id='ms-location_hostgroup_ids')

    @View.nested
    class organizations(SatVerticalTab):
        resources = MultiSelect(id='ms-location_organization_ids')

    @View.nested
    class parameters(SatVerticalTab):
        resources = CustomParameter(id='global_parameters_table')
