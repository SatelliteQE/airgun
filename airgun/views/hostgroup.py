from widgetastic.widget import ConditionalSwitchableView, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Button as PF4Button, Pagination as PF4Pagination

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import (
    ActionsDropdown,
    ConfigGroupMultiSelect,
    FilteredDropdown,
    MultiSelect,
    MultiSelectNoFilter,
    PuppetClassesMultiSelect,
    RadioGroup,
)


class ActivationKeyDropDown(ActionsDropdown):
    dropdown = Text('.//*[self::div]')

    @property
    def items(self):
        """Returns a list of all dropdown items as strings."""
        self.dropdown.click()
        return [
            self.browser.text(el) for el in self.browser.elements(self.ITEMS_LOCATOR, parent=self)
        ]


class HostGroupsView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text(
        "//h1[contains(., 'Host Group Configuration') or normalize-space(.)='Host Groups']"
    )
    new = Text("//a[contains(@href, '/hostgroups/new')]")
    new_on_blank_page = PF4Button('Create Host Group')
    table = Table(
        './/table',
        column_widgets={
            'Name': Text("./a"),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False
        ) is not None and self.browser.url.endswith('hostgroups')


class HostGroupCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Host Groups'
            and self.breadcrumb.read() == 'Create Host Group'
        )

    @View.nested
    class host_group(SatTab):
        TAB_NAME = 'Host Group'

        parent_name = FilteredDropdown(id='s2id_hostgroup_parent_id')
        name = TextInput(id='hostgroup_name')
        description = TextInput(id='hostgroup_description')
        lce = FilteredDropdown(id='hostgroup_lifecycle_environment')
        content_view = FilteredDropdown(id='hostgroup_content_view')
        content_source = FilteredDropdown(id='s2id_content_source_id')
        puppet_environment = FilteredDropdown(id='hostgroup_puppet_attributes_environment')
        deploy = FilteredDropdown(id='hostgroup_compute_resource')
        puppet_master = FilteredDropdown(id='hostgroup_puppet_proxy')
        puppet_ca = FilteredDropdown(id='hostgroup_puppet_ca_proxy')
        openscap_capsule = FilteredDropdown(id='hostgroup_openscap_proxy')

    @View.nested
    class ansible_roles(SatTab):
        TAB_NAME = 'Ansible Roles'
        resources = MultiSelectNoFilter(id='ansible_roles')
        pagination = PF4Pagination()

    @View.nested
    class puppet_enc(SatTab):
        TAB_NAME = 'Puppet ENC'
        config_groups = ConfigGroupMultiSelect(locator='.')
        classes = PuppetClassesMultiSelect(locator='.')

    @View.nested
    class network(SatTab):
        domain = FilteredDropdown(id='hostgroup_domain')
        ipv4_subnet = FilteredDropdown(id='hostgroup_subnet')
        ipv6_subnet = FilteredDropdown(id='hostgroup_subnet6')
        realm = FilteredDropdown(id='hostgroup_realm')

    @View.nested
    class operating_system(SatTab):
        TAB_NAME = 'Operating System'

        architecture = FilteredDropdown(id='hostgroup_architecture')
        operating_system = FilteredDropdown(id='hostgroup_operatingsystem')
        media_type = RadioGroup(locator="//div[label[contains(., 'Media Selection')]]")
        media_content = ConditionalSwitchableView(reference='media_type')

        @media_content.register('All Media')
        class TypeMedium(View):
            media = FilteredDropdown(id='hostgroup_medium')

        @media_content.register('Synced Content')
        class TypeSynced(View):
            synced_content = FilteredDropdown(id='host_group_kickstart_repository')

        ptable = FilteredDropdown(id='hostgroup_ptable')
        root_password = TextInput(id='hostgroup_root_pass')

    @View.nested
    class parameters(SatTab):
        pass

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-hostgroup_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-hostgroup_organization_ids')

    @View.nested
    class activation_keys(SatTab):
        TAB_NAME = 'Activation Keys'
        activation_keys = ActivationKeyDropDown(
            locator=".//foreman-react-component[contains(@data-props, 'kt_activation_keys')]"
        )


class HostGroupEditView(HostGroupCreateView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Host Groups'
            and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class ansible_roles(SatTab):
        TAB_NAME = 'Ansible Roles'
        more_item = Text('//span[@class="pf-c-options-menu__toggle-button-icon"]')
        select_pages = Text('//ul[@class="pf-c-options-menu__menu"]/li[6]/button')
        available_role = '//div[@class="available-roles-container col-sm-6"]/div[2]/div'
        assigned_role = '//div[@class="assigned-roles-container col-sm-6"]/div[2]/div'
        assigned_ansible_role = '//div[@class="assigned-roles-container col-sm-6"]/div[2]/div'
        no_of_available_role = Text('//span[@class="pf-c-options-menu__toggle-text"]//b[2]')
        resources = MultiSelectNoFilter(id='ansible_roles')
        submit = Text('//input[@name="commit"]')
