from widgetastic.widget import Checkbox, Text, TextInput, View

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
    SatVerticalTab,
)
from airgun.widgets import (
    ActionsDropdown,
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
    SatTable,
)


class OrganizationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Organizations']")
    new = Text("//a[contains(@href, '/organizations/new')]")
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


class OrganizationCreateView(BaseLoggedInView):
    name = TextInput(id='organization_name')
    label = TextInput(id='organization_label')
    description = TextInput(id='organization_description')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.submit, exception=False) is not None


class OrganizationCreateSelectHostsView(BaseLoggedInView):
    assign_all = Text("//a[text()='Assign All']")
    assign_manually = Text("//a[text()='Manually Assign']")
    proceed = Text("//a[text()='Proceed to Edit']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.proceed, exception=False) is not None


class OrganizationEditView(BaseLoggedInView):
    submit = Text("//form[contains(@id, 'edit')]//input[@name='commit']")
    cancel = Text("//a[text()='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.submit, exception=False) is not None

    @View.nested
    class primary(SatVerticalTab):
        name = TextInput(id='organization_name')
        default_system_sla = FilteredDropdown(id='organization_service_level')
        description = TextInput(id='organization_description')

    @View.nested
    class users(SatVerticalTab):
        all_users = Checkbox(id='organization_ignore_types_user')
        resources = MultiSelect(id='ms-organization_user_ids')

    @View.nested
    class capsules(SatVerticalTab):
        all_capsules = Checkbox(id='organization_ignore_types_smartproxy')
        resources = MultiSelect(id='ms-organization_smart_proxy_ids')

    @View.nested
    class subnets(SatVerticalTab):
        all_subnets = Checkbox(id='organization_ignore_types_subnet')
        resources = MultiSelect(id='ms-organization_subnet_ids')

    @View.nested
    class compute_resources(SatVerticalTab):
        TAB_NAME = 'Compute Resources'
        all_resources = Checkbox(
            id='organization_ignore_types_computeresource')
        resources = MultiSelect(id='ms-organization_compute_resource_ids')

    @View.nested
    class media(SatVerticalTab):
        all_medias = Checkbox(
            id='organization_ignore_types_medium')
        resources = MultiSelect(id='ms-organization_medium_ids')

    @View.nested
    class provisioning_templates(SatVerticalTab):
        TAB_NAME = 'Provisioning Templates'
        all_tamplates = Checkbox(
            id='organization_ignore_types_provisioningtemplate')
        resources = MultiSelect(id='ms-organization_provisioning_template_ids')

    @View.nested
    class partition_tables(SatVerticalTab):
        TAB_NAME = 'Partition Tables'
        all_ptables = Checkbox(id='organization_ignore_types_ptable')
        resources = MultiSelect(id='ms-organization_ptable_ids')

    @View.nested
    class domains(SatVerticalTab):
        all_domains = Checkbox(id='organization_ignore_types_domain')
        resources = MultiSelect(id='ms-organization_domain_ids')

    @View.nested
    class realms(SatVerticalTab):
        all_realms = Checkbox(id='organization_ignore_types_realm')
        resources = MultiSelect(id='ms-organization_realm_ids')

    @View.nested
    class environments(SatVerticalTab):
        all_environments = Checkbox(id='organization_ignore_types_environment')
        resources = MultiSelect(id='ms-organization_environment_ids')

    @View.nested
    class host_groups(SatVerticalTab):
        TAB_NAME = 'Host Groups'
        all_hostgroups = Checkbox(id='organization_ignore_types_hostgroup')
        resources = MultiSelect(id='ms-organization_hostgroup_ids')

    @View.nested
    class locations(SatVerticalTab):
        resources = MultiSelect(id='ms-organization_location_ids')

    @View.nested
    class parameters(SatVerticalTab):
        resources = CustomParameter()
