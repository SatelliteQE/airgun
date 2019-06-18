import re
from wait_for import wait_for

from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    GenericLocatorWidget,
    NoSuchElementException,
    Select,
    Text,
    Table,
    TextInput,
    View,
    Widget,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.views.job_invocation import JobInvocationCreateView, JobInvocationStatusView
from airgun.widgets import (
    ActionsDropdown,
    CheckboxWithAlert,
    ConfigGroupMultiSelect,
    CustomParameter,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    Link,
    MultiSelect,
    PuppetClassesMultiSelect,
    RadioGroup,
    RemovableWidgetsItemsListView,
    SatTableWithUnevenStructure,
    SatTable,
    ToggleButton,
)


class TableActions(View):
    """Interface table has Action column that contains only two buttons,
    without any extra controls, so we cannot re-use any existing widgets
    """
    edit = Button('Edit')
    delete = Button('Delete')


class PuppetClassParameterValue(Widget):
    """Represent value field for Puppet Class parameters table row from Host
    Parameters tab. That field can be interacted with as usual text input, but
    also it can be overridden with new value
    """
    ROOT = ".//div[@class='input-group']"
    value = TextInput(
        locator=".//*[self::textarea or self::input][contains(@name, 'lookup_values_attributes')]")
    override_button = Text(".//a[@data-tag='override']")
    remove_override_button = Text(".//a[@data-tag='remove']")
    hide_button = Text(".//a[contains(@class, 'btn-hide')]")

    @property
    def hidden(self):
        """Return whether the variable is hidden"""
        return 'masked-input' in self.browser.classes(self.value)

    @property
    def overridden(self):
        """Return whether the variable is overridden, a variable is overridden if not disabled"""
        return self.browser.get_attribute('disabled', self.value) is None

    @property
    def hidden_value(self):
        return self.browser.get_attribute('data-hidden-value', self.value)

    def read(self):
        """Return smart variable widget values"""
        return {'value': self.value.read(), 'overridden': self.overridden, 'hidden': self.hidden,
                'hidden_value': self.hidden_value}

    def fill(self, value):
        """Set smart variable widget values"""
        overridden = None
        hidden = None
        if isinstance(value, dict):
            overridden = value.get('overridden')
            hidden = value.get('hidden')
            value = value.get('value')
        if hidden is not None:
            self.hide(hidden)
        if overridden is not None:
            self.override(overridden)
        if value is not None:
            self.value.fill(value)

    def hide(self, value=True):
        """Hide or unhide the smart variable input box"""
        if value != self.hidden:
            self.hide_button.click()

    def override(self, value=True):
        """Click corresponding button depends on action needed"""
        overridden = self.overridden
        if value and not overridden:
            self.override_button.click()
        elif not value and overridden:
            self.remove_override_button.click()


class ComputeResourceLibvirtProfileStorageItem(GenericRemovableWidgetItem):
    """Libvirt Compute Resource profile "Storage" item widget"""
    storage_pool = FilteredDropdown(id="pool_name")
    size = TextInput(locator=".//input[contains(@id, 'capacity')]")
    storage_type = FilteredDropdown(id="format_type")


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

    # Compute resource attributes
    network_type = FilteredDropdown(id='_compute_attributes_type')
    network = FilteredDropdown(id='_compute_attributes_bridge')
    nic_type = FilteredDropdown(id='_compute_attributes_model')

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
    export = Text(
        ".//a[contains(@class, 'btn')][contains(@href, 'hosts.csv')]")
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
            and self.breadcrumb.locations[0] == 'All Hosts'
            and self.breadcrumb.read() == 'Create Host'
        )

    @View.nested
    class host(SatTab):
        name = TextInput(id='host_name')
        organization = FilteredDropdown(id='host_organization')
        location = FilteredDropdown(id='host_location')
        hostgroup = FilteredDropdown(id='host_hostgroup')
        inherit_deploy_option = ToggleButton(
            locator=".//div[label[@for='compute_resource_id']]//button")
        deploy = FilteredDropdown(id='host_compute_resource')
        lce = FilteredDropdown(id='host_lifecycle_environment')
        content_view = FilteredDropdown(id='host_content_view')
        content_source = FilteredDropdown(id='s2id_content_source_id')
        reset_puppet_environment = Link(".//a[@id='reset_puppet_environment']")
        inherit_puppet_environment = ToggleButton(
            locator=".//div[label[@for='environment_id']]//button")
        puppet_environment = FilteredDropdown(id='host_environment')
        puppet_master = FilteredDropdown(id='host_puppet_proxy')
        puppet_ca = FilteredDropdown(id='host_puppet_ca_proxy')
        openscap_capsule = FilteredDropdown(id='host_openscap_proxy')

    @View.nested
    class ansible_roles(SatTab):
        TAB_NAME = 'Ansible Roles'

        resources = MultiSelect(id='ms-host_ansible_role_ids')

    @property
    def current_provider(self):
        """Retrieve the provider name from the compute resource name.

        Note: The provider name is always appended to the end of the compute resource name,
        for example: compute resource name "foo"

        1. For RHV provider, the compute resource name will be displayed as: "foo (RHV)"
        2. For Libvirt provider, the compute resource name will be displayed as: "foo (Libvirt)"

        Return "Compute resource is not specified" value in case no compute resource specified
        in deployment procedure (e.g. "Bare Metal")
        """
        try:
            compute_resource_name = self.host.deploy.read()
        except NoSuchElementException:
            return 'Compute resource is not specified'
        return re.findall(r'.*\((?:.*-)*(.*?)\)\Z|$', compute_resource_name)[0]

    provider_content = ConditionalSwitchableView(reference='current_provider')

    @provider_content.register('Compute resource is not specified', default=True)
    class NoResourceForm(View):
        pass

    @provider_content.register('Libvirt')
    class LibvirtResourceForm(View):

        @View.nested
        class virtual_machine(SatTab):
            TAB_NAME = 'Virtual Machine'
            cpus = TextInput(id='host_compute_attributes_cpus')
            cpu_mode = FilteredDropdown(id='s2id_host_compute_attributes_cpu_mode')
            memory = TextInput(id='host_compute_attributes_memory')
            startup = Checkbox(id='host_compute_attributes_start')

            @View.nested
            class storage(RemovableWidgetsItemsListView):
                ROOT = "//fieldset[@id='storage_volumes']"
                ITEMS = "./div/div[contains(@class, 'removable-item')]"
                ITEM_WIDGET_CLASS = ComputeResourceLibvirtProfileStorageItem

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
            push 'Edit' button to open necessary dialog to be able to fill values
            """
            self.interfaces_list[0]['Actions'].widget.edit.click()
            wait_for(
                lambda: self.interface.is_displayed is True,
                timeout=30,
                delay=1,
                logger=self.logger
            )

    @View.nested
    class puppet_classes(SatTab):
        TAB_NAME = 'Puppet Classes'
        config_groups = ConfigGroupMultiSelect(locator='.')
        classes = PuppetClassesMultiSelect(locator='.')

    @View.nested
    class parameters(SatTab):
        """Host parameters tab"""
        puppet_class_parameters = Table(
            ".//table[@id='inherited_puppetclasses_parameters']",
            column_widgets={'Value': PuppetClassParameterValue()}
        )

        @View.nested
        class global_params(SatTable):

            def __init__(self, parent, **kwargs):
                locator = ".//table[@id='inherited_parameters']"
                column_widgets = {
                    'Name': Text(
                        locator=".//span[starts-with(@id, 'name_')]"),
                    'Value': TextInput(
                        locator=".//textarea[@data-property='value']"),
                    'Actions': Text(
                        locator=(".//a[@data-original-title"
                                 "='Override this value']")
                    )
                }
                SatTable.__init__(self, parent, locator,
                                  column_widgets=column_widgets, **kwargs)

            def read(self):
                """Return a list of dictionaries. Each dictionary consists of
                global parameter name, value and whether overridden or not.
                """
                parameters = []
                for row in self.rows():
                    parameters.append({
                        'name': row['Name'].widget.read(),
                        'value': row['Value'].widget.read(),
                        'overridden': not row['Actions'].widget.is_displayed
                    })
                return parameters

            def override(self, name):
                """Override a single global parameter.

                :param str name: The name of the global parameter to override.
                """
                for row in self.rows():
                    if (row['Name'].widget.read() == name
                            and row['Actions'].widget.is_displayed):
                        row['Actions'].widget.click()  # click 'Override'
                        break

            def fill(self, names):
                """Override global parameter entries.

                :param list[str] names: global parameters names to override.
                """
                for name in names:
                    self.override(name)

        host_params = CustomParameter(id='global_parameters_table')

        def fill(self, values):
            """Fill the parameters tab widgets with values.

            Args:
                values: A dictionary of ``widget_name: value_to_fill``.

            Note:
                The global_params value can be a list of names of global
                parameters to override or a list of dicts like
                [{name: global_param_name_to_override, value: new_value}...]
            """
            host_params = values.get('host_params')
            global_params = values.get('global_params')
            if global_params:
                new_global_params = []
                if not host_params:
                    host_params = []
                    values['host_params'] = host_params
                for global_param in global_params:
                    if isinstance(global_param, dict):
                        host_params.append(global_param)
                        new_global_params.append(global_param['name'])
                    else:
                        new_global_params.append(global_param)
                values['global_params'] = new_global_params
            return SatTab.fill(self, values)

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
                and self.breadcrumb.locations[0] == 'All Hosts'
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
    yaml_output = Text("//pre")
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
                and self.breadcrumb.locations[0] == 'All Hosts'
                and self.breadcrumb.read().startswith('Edit ')
        )


class HostsActionCommonDialog(BaseLoggedInView):
    """Common base class Dialog for Hosts Actions"""
    title = None
    table = SatTable("//div[@class='modal-body']//table")
    keep_selected = Checkbox(id='keep_selected')
    submit = Text('//button[@onclick="tfm.hosts.table.submitModalForm()"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostsChangeGroup(HostsActionCommonDialog):
    title = Text(
        "//h4[text()='Change Group - The"
        " following hosts are about to be changed']")
    host_group = Select(id='hostgroup_id')


class HostsChangeEnvironment(HostsActionCommonDialog):
    title = Text(
        "//h4[text()='Change Environment - The"
        " following hosts are about to be changed']")
    environment = Select(id='environment_id')


class HostsTaxonomyMismatchRadioGroup(GenericLocatorWidget):
    """Handle Taxonomy Mismatch Radio Group

    Example html representation::

        <form ...>
            <div class="clearfix">
                ...
            </div>
            <input type="radio" id="location_optimistic_import_yes" ..>
             Fix Location on Mismatch
            <input type="radio" id="location_optimistic_import_no" ..>
             Fail on Mismatch
        </form>
    """
    taxonomy = None
    fix_mismatch = Text("//input[contains(@id, 'optimistic_import_yes')]")
    fail_on_mismatch = Text(
        "//input[contains(@id, 'optimistic_import_no')]")
    buttons_text = dict(
        fix_mismatch='Fix {taxonomy} on Mismatch',
        fail_on_mismatch='Fail on Mismatch'
    )

    def __init__(self, parent, **kwargs):
        self.taxonomy = kwargs.pop('taxonomy')
        super(HostsTaxonomyMismatchRadioGroup, self).__init__(
            parent,
            "//div[@class='modal-body']//div[@id='content']/form",
            **kwargs
        )

    def _is_checked(self, widget):
        """Returns whether the widget is checked"""
        return self.browser.get_attribute('checked', widget) is not None

    def read(self):
        """Return the text of the selected button"""
        for name, text in self.buttons_text.items():
            if self._is_checked(getattr(self, name)):
                return text.replace('{taxonomy}', self.taxonomy)

    def fill(self, value):
        """Select the button with text equal to value"""
        for name, text in self.buttons_text.items():
            text = text.replace('{taxonomy}', self.taxonomy)
            widget = getattr(self, name)
            if text == value and not self._is_checked(widget):
                widget.click()

    @property
    def is_displayed(self):
        return (self.fix_mismatch.is_displayed
                and self.fail_on_mismatch.is_displayed)


class HostsAssignOrganization(HostsActionCommonDialog):
    title = Text(
        "//h4[text()='Assign Organization"
        " - The following hosts are about to be changed']")
    organization = Select(id='organization_id')
    on_mismatch = HostsTaxonomyMismatchRadioGroup(taxonomy='Organization')


class HostsAssignLocation(HostsActionCommonDialog):
    title = Text(
        "//h4[text()='Assign Location"
        " - The following hosts are about to be changed']")
    location = Select(id='location_id')
    on_mismatch = HostsTaxonomyMismatchRadioGroup(taxonomy='Location')


class HostsAssignCompliancePolicy(HostsActionCommonDialog):
    title = Text(
        "//h4[text()='Assign Compliance Policy"
        " - The following hosts are about to be changed']")
    policy = Select(id='policy_id')


class HostsDeleteActionDialog(HostsActionCommonDialog):
    title = Text("//h4[text()='Delete Hosts - The following hosts are about to be changed']")


class HostsJobInvocationCreateView(JobInvocationCreateView):
    """Hosts Job Invocation Create View"""


class HostsJobInvocationStatusView(JobInvocationStatusView):
    """Hosts Job Invocation Status View"""
