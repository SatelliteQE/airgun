from wait_for import wait_for

from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import (
    ActionsDropdown,
    CheckboxWithAlert,
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
    RadioGroup,
    SatTableWithUnevenStructure,
    SatTable,
)


class TableActions(View):
    """Interface table has Action column that contains only two buttons,
    without any extra controls, so we cannot re-use any existing widgets
    """
    edit = Text(".//button[contains(., 'Edit')]")
    delete = Text(".//button[contains(., 'Delete')]")


class HostInterface(View):
    ROOT = ".//div[@id='interfaceModal']"
    title = Text(".//h4[contains(., 'Interface')]")
    submit = Text(".//button[contains(@onclick, 'save_interface_modal')]")
    interface_type = FilteredDropdown(id='_type')
    mac = TextInput(locator=".//input[contains(@id, '_mac')]")
    device_identifier = TextInput(
        locator=".//input[contains(@id, '_identifier')]")
    dns = TextInput(locator=".//input[contains(@id, '_name')]")
    domain = FilteredDropdown(id='_domain_id')
    subnet = FilteredDropdown(id='_subnet_id')
    subnet_v6 = FilteredDropdown(id='_subnet6_id')
    ip = TextInput(locator=".//input[contains(@id, '_ip')]")
    ipv6 = TextInput(locator=".//input[contains(@id, '_ip6')]")
    managed = Checkbox(locator=".//input[contains(@id, '_managed')]")
    primary = CheckboxWithAlert(locator=".//input[contains(@id, '_primary')]")
    provision = CheckboxWithAlert(
        locator=".//input[contains(@id, '_provision')]")
    remote_execution = Checkbox(
        locator=".//input[contains(@id, '_execution')]")
    # when interface type is selected, some additional controls will appear on
    # the page
    interface_additional_data = ConditionalSwitchableView(
        reference='interface_type')

    @interface_additional_data.register('Interface')
    class InterfaceForm(View):
        virtual_nic = Checkbox(
            locator=".//input[contains(@id, '_virtual')]")
        virtual_attributes = ConditionalSwitchableView(
            reference='virtual_nic')

        @virtual_attributes.register(True, default=True)
        class VirtualAttributesForm(View):
            tag = TextInput(locator=".//input[contains(@id, '_tag')]")
            attached_to = TextInput(
                locator=".//input[contains(@id, '_attached_to')]")

    @interface_additional_data.register('BMC')
    class BMCForm(View):
        username = TextInput(locator=".//input[contains(@id, '_username')]")
        password = TextInput(locator=".//input[contains(@id, '_password')]")
        provider = FilteredDropdown(id='_provider')

    @interface_additional_data.register('Bond')
    class BondForm(View):
        mode = FilteredDropdown(id='_mode')
        attached_devices = TextInput(
            locator=".//input[contains(@id, '_attached_devices')]")
        bond_options = TextInput(
            locator=".//input[contains(@id, '_bond_options')]")

    @interface_additional_data.register('Bridge')
    class BridgeForm(View):
        attached_devices = TextInput(
            locator=".//input[contains(@id, '_attached_devices')]")

    def after_fill(self, was_change):
        """Submit the dialog data once all necessary view widgets filled"""
        self.submit.click()
        wait_for(
            lambda: self.submit.is_displayed is False,
            timeout=300,
            delay=1,
            logger=self.logger
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, visible=True, exception=False) is not None


class HostsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Hosts']")
    new = Text("//a[contains(@href, '/hosts/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            0: Checkbox(
                locator=".//input[@class='host_select_boxes']"),
            'Name': Text("./a"),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )
    actions = ActionsDropdown("//div[@id='submit_multiple']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Hosts'
                and self.breadcrumb.read() == 'Create Host'
        )

    @View.nested
    class host(SatTab):
        name = TextInput(id='host_name')
        organization = FilteredDropdown(id='host_organization')
        location = FilteredDropdown(id='host_location')
        hostgroup = FilteredDropdown(id='host_hostgroup')
        deploy = FilteredDropdown(id='host_compute_resource')
        lce = FilteredDropdown(id='host_lifecycle_environment')
        content_view = FilteredDropdown(id='host_content_view')
        content_source = FilteredDropdown(id='s2id_content_source_id')
        puppet_environment = FilteredDropdown(id='host_environment')
        puppet_master = FilteredDropdown(id='host_puppet_proxy')
        puppet_ca = FilteredDropdown(id='host_puppet_ca_proxy')
        openscap_capsule = FilteredDropdown(id='host_openscap_proxy')

    @View.nested
    class ansible_roles(SatTab):
        TAB_NAME = 'Ansible Roles'

        resources = MultiSelect(id='ms-host_ansible_role_ids')

    @View.nested
    class operating_system(SatTab):
        TAB_NAME = 'Operating System'

        architecture = FilteredDropdown(id='host_architecture')
        operating_system = FilteredDropdown(id='host_operatingsystem')
        build = Checkbox(id='host_build')
        media_type = RadioGroup(
            locator="//div[label[contains(., 'Media Selection')]]")
        media = FilteredDropdown(id='host_medium')
        ptable = FilteredDropdown(id='host_ptable')
        disk = TextInput(id='host_disk')
        root_password = TextInput(id='host_root_pass')

    @View.nested
    class interfaces(SatTab):
        interface = HostInterface()
        interfaces_list = SatTable(
            ".//table[@id='interfaceList']",
            column_widgets={'Actions': TableActions()}
        )
        add_new_interface = Text("//button[@id='addInterface']")

        def before_fill(self, values=None):
            """If we don't want to break view.fill() procedure flow, we need to
            push 'Add Interface' button to open necessary dialog to be able to
            fill values
            """
            self.interfaces_list[0]['Actions'].widget.edit.click()
            wait_for(
                lambda: self.interface.is_displayed is True,
                timeout=300,
                delay=1,
                logger=self.logger
            )

    @View.nested
    class puppet_classes(SatTab):
        TAB_NAME = 'Puppet Classes'

        pass

    @View.nested
    class parameters(SatTab):
        host_params = CustomParameter(id='global_parameters_table')

    @View.nested
    class additional_information(SatTab):
        TAB_NAME = 'Additional Information'

        owned_by = FilteredDropdown(id='host_is_owned_by')
        enabled = Checkbox(id='host_enabled')
        hardware_model = FilteredDropdown(id='host_model_id')
        comment = TextInput(id='host_comment')


class HostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Hosts'
                and self.breadcrumb.read() != 'Create Host'
        )

    boot_disk = ActionsDropdown(
        "//div[contains(@class, 'btn-group')]"
        "[contains(., 'Boot')][not(*[self::div])]"
    )
    schedule_remote_job = ActionsDropdown(
        "//div[contains(@class, 'btn-group')]"
        "[contains(., 'Schedule')][not(*[self::div])]"
    )
    back = Text("//a[text()='Back']")
    edit = Text("//a[@id='edit-button']")
    clone = Text("//a[@id='clone-button']")
    build = Text("//a[@id='build-review']")
    delete = Text("//a[@id='delete-button']")
    audits_details = Text("//a[text()='Audits']")
    facts_details = Text("//a[text()='Facts']")
    yaml_dump = Text("//a[text()='YAML']")
    content_details = Text("//a[text()='Content']")

    @View.nested
    class properties(SatTab):
        properties_table = SatTableWithUnevenStructure(
            locator="//table[@id='properties_table']")


class HostEditView(HostCreateView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    toggle_manage = Text("//a[contains(@href, '/toggle_manage')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Hosts'
                and self.breadcrumb.read().starts_with('Edit ')
        )


class HostsChangeGroup(View):
    title = Text(
        "//h4[text()='Change Group - The"
        " following hosts are about to be changed']")
    table = SatTable("//div[@class='modal-body']//table")
    keep_selected = Checkbox(id='keep_selected')
    host_group = Select(id='hostgroup_id')
    submit = Text('//button[@onclick="submit_modal_form()"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def after_fill(self, was_change):
        """Submit the dialog data once all necessary view widgets filled"""
        self.submit.click()
        wait_for(
            lambda: self.submit.is_displayed is False,
            timeout=300,
            delay=1,
            logger=self.logger
        )


class HostsChangeEnvironment(View):
    title = Text(
        "//h4[text()='Change Environment - The"
        " following hosts are about to be changed']")
    table = SatTable("//div[@class='modal-body']//table")
    keep_selected = Checkbox(id='keep_selected')
    environment = Select(id='environment_id')
    submit = Text('//button[@onclick="submit_modal_form()"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def after_fill(self, was_change):
        """Submit the dialog data once all necessary view widgets filled"""
        self.submit.click()
        wait_for(
            lambda: self.submit.is_displayed is False,
            timeout=300,
            delay=1,
            logger=self.logger
        )
