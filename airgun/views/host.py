import re
import time

from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    GenericLocatorWidget,
    NoSuchElementException,
    Select,
    Table,
    Text,
    TextInput,
    View,
    Widget,
)
from widgetastic_patternfly import BreadCrumb, Button
from widgetastic_patternfly4.ouia import (
    BreadCrumb as PF4BreadCrumb,
    Button as PF4Button,
)
from widgetastic_patternfly5.components.tabs import Tab
from widgetastic_patternfly5.ouia import (
    Button as PF5Button,
    FormSelect as PF5FormSelect,
    PatternflyTable as PF5OUIATable,
    Select as PF5OUIASelect,
    TextInput as PF5OUIATextInput,
)

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.views.host_new import MenuToggleButtonMenu
from airgun.views.job_invocation import JobInvocationCreateView, JobInvocationStatusView
from airgun.views.task import TaskDetailsView
from airgun.widgets import (
    ActionsDropdown,
    BaseMultiSelect,
    CheckboxWithAlert,
    ConfigGroupMultiSelect,
    CustomParameter,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    Link,
    MultiSelect,
    Pf4ConfirmationDialog,
    PuppetClassesMultiSelect,
    RadioGroup,
    RemovableWidgetsItemsListView,
    SatTable,
    SatTableWithUnevenStructure,
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
        locator=".//*[self::textarea or self::input][contains(@name, 'lookup_values_attributes')]"
    )
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
        return {
            'value': self.value.read(),
            'overridden': self.overridden,
            'hidden': self.hidden,
            'hidden_value': self.hidden_value,
        }

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

    storage_pool = FilteredDropdown(id='pool_name')
    size = TextInput(locator=".//input[contains(@id, 'capacity')]")
    storage_type = FilteredDropdown(id='format_type')


class ComputeResourceGoogleProfileStorageItem(GenericRemovableWidgetItem):
    """Google Compute Resource profile "Storage" item widget"""

    size = TextInput(locator=".//input[contains(@id, 'size')]")


class HostInterface(View):
    ROOT = ".//div[@id='interfaceModal']"
    title = Text(".//h4[contains(., 'Interface')]")
    submit = Text(".//button[contains(@onclick, 'save_interface_modal')]")
    interface_type = FilteredDropdown(id='_type')
    mac = TextInput(locator=".//input[contains(@id, '_mac')]")
    device_identifier = TextInput(locator=".//input[contains(@id, '_identifier')]")
    dns = TextInput(locator=".//input[contains(@id, '_name')]")
    domain = FilteredDropdown(id='_domain_id')
    subnet = FilteredDropdown(id='_subnet_id')
    subnet_v6 = FilteredDropdown(id='_subnet6_id')
    ip = TextInput(locator=".//input[contains(@id, '_ip')]")
    ipv6 = TextInput(locator=".//input[contains(@id, '_ip6')]")
    managed = Checkbox(locator=".//input[contains(@id, '_managed')]")
    primary = CheckboxWithAlert(locator=".//input[contains(@id, '_primary')]")
    provision = CheckboxWithAlert(locator=".//input[contains(@id, '_provision')]")
    remote_execution = Checkbox(locator=".//input[contains(@id, '_execution')]")
    # when interface type is selected, some additional controls will appear on
    # the page
    interface_additional_data = ConditionalSwitchableView(reference='interface_type')

    @interface_additional_data.register('Interface')
    class InterfaceForm(View):
        virtual_nic = Checkbox(locator=".//input[contains(@id, '_virtual')]")
        virtual_attributes = ConditionalSwitchableView(reference='virtual_nic')

        @virtual_attributes.register(True, default=True)
        class VirtualAttributesForm(View):
            tag = TextInput(locator=".//input[contains(@id, '_tag')]")
            attached_to = TextInput(locator=".//input[contains(@id, '_attached_to')]")

    @interface_additional_data.register('BMC')
    class BMCForm(View):
        username = TextInput(locator=".//input[contains(@id, '_username')]")
        password = TextInput(locator=".//input[contains(@id, '_password')]")
        provider = FilteredDropdown(id='_provider')

    @interface_additional_data.register('Bond')
    class BondForm(View):
        mode = FilteredDropdown(id='_mode')
        attached_devices = TextInput(locator=".//input[contains(@id, '_attached_devices')]")
        bond_options = TextInput(locator=".//input[contains(@id, '_bond_options')]")

    @interface_additional_data.register('Bridge')
    class BridgeForm(View):
        attached_devices = TextInput(locator=".//input[contains(@id, '_attached_devices')]")

    # Compute resource attributes
    network_type = FilteredDropdown(id='_compute_attributes_type')
    network = FilteredDropdown(id='_compute_attributes_bridge')
    nic_type = FilteredDropdown(id='_compute_attributes_model')

    def after_fill(self, was_change):
        """Submit the dialog data once all necessary view widgets filled"""
        self.submit.click()
        wait_for(
            lambda: self.submit.is_displayed is False, timeout=300, delay=1, logger=self.logger
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, visible=True, exception=False) is not None


class HostStatusesView(BaseLoggedInView):
    title = Text("//h5[normalize-space(.)='Host Status Overview']")
    status_green_total = Text("//div[contains(@class, 'status-count')][1]/a[1]")
    status_green_owned = Text("//div[contains(@class, 'status-count')][1]/a[2]")
    status_yellow_total = Text("//div[contains(@class, 'status-count')][2]/span[1]")
    status_yellow_owned = Text("//div[contains(@class, 'status-count')][2]/span[2]")
    status_red_total = Text("//div[contains(@class, 'status-count')][3]/a[1]")
    status_red_owned = Text("//div[contains(@class, 'status-count')][3]/a[2]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class HostsView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Hosts']")
    manage_columns = PF5Button('manage-columns-button')
    export = Text(".//a[contains(@class, 'btn')][contains(@href, 'hosts.csv')]")
    new = Text(".//div[@id='foreman-page']//a[@data-ouia-component-id='create-host-button']")
    register = PF4Button('OUIA-Generated-Button-secondary-2')
    new_ui_button = Text(".//a[contains(@class, 'btn')][contains(@href, 'new/hosts')]")
    select_all = Checkbox(locator="//input[@id='check_all']")
    table = PF5OUIATable(
        component_id='hosts-index-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text(
                ".//a[contains(@href, '/new/hosts/') and not(contains(@href, 'Red Hat Lightspeed'))]"
            ),
            'Recommendations': Text('./a'),
            6: MenuToggleButtonMenu(),
        },
    )
    displayed_table_headers = './/table/thead/tr/th[not(@hidden)]'
    host_status = "//span[contains(@class, 'host-status')]"
    actions = ActionsDropdown("//div[@id='submit_multiple']")
    dialog = Pf4ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    @property
    def displayed_table_header_names(self) -> list:
        """
        Return names of the displayed headers in the hosts table.

        Note: Cannot use 'self.table.headers' for this because it returns also hidden headers.
        """
        return [
            header.text.strip() for header in self.browser.elements(self.displayed_table_headers)
        ]


class HostCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
            locator=".//div[label[@for='compute_resource_id']]//button"
        )
        deploy = FilteredDropdown(id='host_compute_resource')
        inherit_compute_profile_option = ToggleButton(
            locator=".//div[label[@for='compute_profile_id']]//button"
        )
        compute_profile = FilteredDropdown(id='host_compute_profile_id')
        lce = FilteredDropdown(id='host_lifecycle_environment')
        content_view = FilteredDropdown(id='host_content_view')
        content_source = FilteredDropdown(id='content_source_id')
        reset_puppet_environment = Link(".//a[@id='reset_puppet_environment']")
        inherit_puppet_environment = ToggleButton(
            locator=".//div[label[@for='environment_id']]//button"
        )
        puppet_environment = FilteredDropdown(id='host_puppet_attributes_environment')
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

        1. For Libvirt provider, the compute resource name will be displayed as: "foo (Libvirt)"

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
            provision_method = Checkbox(id='host_provision_method_image')

    @provider_content.register('Google')
    class GoogleResourceForm(View):
        @View.nested
        class virtual_machine(SatTab):
            TAB_NAME = 'Virtual Machine'
            machine_type = FilteredDropdown(id='host_compute_attributes_machine_type')
            network = FilteredDropdown(id='host_compute_attributes_network')
            external_ip = Checkbox(id='host_compute_attributes_associate_external_ip')

            @View.nested
            class storage(RemovableWidgetsItemsListView):
                ROOT = "//fieldset[@id='storage_volumes']"
                ITEMS = "./div/div[contains(@class, 'removable-item')]"
                ITEM_WIDGET_CLASS = ComputeResourceGoogleProfileStorageItem

    @provider_content.register('Azure Resource Manager')
    class AzureRmResourceForm(View):
        @View.nested
        class virtual_machine(SatTab):
            TAB_NAME = 'Virtual Machine'
            resource_group = FilteredDropdown(id='azure_rm_rg')
            vm_size = FilteredDropdown(id='azure_rm_size')
            platform = FilteredDropdown(id='host_compute_attributes_platform')
            username = TextInput(id='host_compute_attributes_username')
            password = TextInput(id='host_compute_attributes_password')
            ssh_key = TextInput(id='host_compute_attributes_ssh_key_data')
            premium_os_disk = Checkbox(id='host_compute_attributes_premium_os_disk')
            os_disk_caching = FilteredDropdown(id='host_compute_attributes_os_disk_caching')
            custom_script_command = TextInput(id='host_compute_attributes_script_command')
            file_uris = TextInput(id='host_compute_attributes_script_uris')

        @View.nested
        class operating_system(SatTab):
            TAB_NAME = 'Operating System'

            architecture = FilteredDropdown(id='host_architecture_id')
            operating_system = FilteredDropdown(id='host_operatingsystem_id')
            image = FilteredDropdown(id='azure_rm_image_id')
            root_password = TextInput(id='host_root_pass')

    @View.nested
    class operating_system(SatTab):
        TAB_NAME = 'Operating System'

        architecture = FilteredDropdown(id='host_architecture')
        operating_system = FilteredDropdown(id='host_operatingsystem')
        build = Checkbox(id='host_build')
        image = FilteredDropdown(id='host_compute_attributes_image')
        media_type = RadioGroup(locator="//div[label[contains(., 'Media Selection')]]")
        media = FilteredDropdown(id='host_medium')
        ptable = FilteredDropdown(id='host_ptable')
        disk = TextInput(id='host_disk')
        root_password = TextInput(id='host_root_pass')
        disable_passwd = Text('//a[@id="disable-pass-btn"]')

    @View.nested
    class interfaces(SatTab):
        interface = HostInterface()
        interfaces_list = SatTable(
            ".//table[@id='interfaceList']", column_widgets={'Actions': TableActions()}
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
                logger=self.logger,
            )

    @View.nested
    class puppet_enc(SatTab):
        TAB_NAME = 'Puppet ENC'

        config_groups = ConfigGroupMultiSelect(locator='.')
        classes = PuppetClassesMultiSelect(locator='.')

        puppet_class_parameters = Table(
            ".//table[@id='puppet_klasses_parameters_table']",
            column_widgets={'Value': PuppetClassParameterValue()},
        )

    @View.nested
    class parameters(SatTab):
        """Host parameters tab"""

        @View.nested
        class global_params(SatTable):
            def __init__(self, parent, **kwargs):
                locator = ".//table[@id='inherited_parameters']"
                column_widgets = {
                    'Name': Text(locator=".//span[starts-with(@id, 'name_')]"),
                    'Value': TextInput(locator=".//textarea[@data-property='value']"),
                    'Actions': Text(
                        locator=(
                            ".//a[@data-original-title='Override this value' "
                            "or @title='Override this value']"
                        )
                    ),
                }
                SatTable.__init__(self, parent, locator, column_widgets=column_widgets, **kwargs)

            def read(self):
                """Return a list of dictionaries. Each dictionary consists of
                global parameter name, value and whether overridden or not.
                """
                return [
                    {
                        'name': row['Name'].widget.read(),
                        'value': row['Value'].widget.read(),
                        'overridden': not row['Actions'].widget.is_displayed,
                    }
                    for row in self.rows()
                ]

            def override(self, name):
                """Override a single global parameter.

                :param str name: The name of the global parameter to override.
                """
                for row in self.rows():
                    if row['Name'].widget.read() == name and row['Actions'].widget.is_displayed:
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


class HostRegisterView(BaseLoggedInView):
    title = Text("//h1[normalize-space(.)='Register Host']")
    generate_command = PF5Button('registration_generate_btn')
    cancel = PF5Button('registration-cancel-button')
    registration_command = TextInput(locator="//input[@aria-label='Copyable input']")

    @View.nested
    class general(Tab):
        TAB_NAME = 'General'
        TAB_LOCATOR = ParametrizedLocator(
            './/div[contains(@class, "pf-v5-c-tabs")]//ul'
            '/li[button[normalize-space(.)={@tab_name|quote}]]'
        )
        ROOT = '//section[@id="generalSection"]'

        organization = PF5FormSelect('reg_organization')
        location = PF5FormSelect('reg_location')
        host_group = PF5FormSelect('reg_host_group')
        operating_system = PF5FormSelect('os-select')
        linux_host_init_link = Link('//a[normalize-space(.)="Linux host_init_config default"]')
        capsule = PF5FormSelect('reg_smart_proxy')
        insecure = Checkbox(id='reg_insecure')
        activation_keys = BaseMultiSelect('activation-keys-field')
        activation_key_helper = Text(
            locator='//div[@data-ouia-component-id="activation-keys-field"]/..//div[contains(@class, "-c-helper-text")]'
        )
        new_activation_key_link = Link('//a[normalize-space(.)="Create new activation key"]')

    @View.nested
    class advanced(Tab):
        TAB_NAME = 'Advanced'
        TAB_LOCATOR = ParametrizedLocator(
            './/div[contains(@class, "pf-v5-c-tabs")]//ul'
            '/li[button[normalize-space(.)={@tab_name|quote}]]'
        )
        ROOT = '//section[@id="advancedSection"]'
        setup_rex = PF5FormSelect('registration_setup_remote_execution')
        setup_insights = PF5FormSelect('registration_setup_insights')
        install_packages = TextInput(id='reg_packages')
        update_packages = Checkbox(id='reg_update_packages')
        token_life_time = TextInput(id='reg_token_life_time_input')
        rex_interface = TextInput(id='reg_rex_interface_input')
        rex_pull_mode = PF5FormSelect('registration_setup_remote_execution_pull')
        ignore_error = Checkbox(id='reg_katello_ignore')
        force = Checkbox(id='reg_katello_force')
        install_packages_helper = Text(
            locator='//input[@id="reg_packages"]/../..//div[contains(@class, "-c-helper-text")]'
        )
        repository_add = PF5Button('host_reg_add_more_repositories')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False)

    def before_fill(self, values):
        """Fill some of the parameters in the widgets with values.

        Args:
            values: A dictionary of `widget_name: value_to_fill`.

        Note:
            Some of the fields are disabled for few seconds and get enabled based
            on the selection, handled separately
        """
        for field in ('host_group', 'operating_system'):
            field_value = values.get('general').get(field)
            if field_value:
                wait_for(
                    lambda field=field: self.general.__getattribute__(field).is_enabled,
                    timeout=30,
                    delay=2,
                    logger=self.logger,
                )
                self.general.__getattribute__(field).fill(field_value)
                time.sleep(1)


class RepositoryListView(View):
    """Repository List view"""

    ROOT = '//div[@id="pf-modal-part-0" or @data-ouia-component-type="PF5/ModalContent"]'
    repository = PF5OUIATextInput('host_reg_repo')
    repository_gpg_key_url = PF5OUIATextInput('host_reg_gpg_key')
    repository_list_confirm = PF5Button('reg_modal_confirm')
    repository_list_reset = PF5Button('reg_modal_reset')
    repository_list_add_new = PF5Button('host_reg_modal_add_new_repo')
    repository_list_remove = PF5Button('0')
    repository_list_popup_close = PF5Button('host_reg_repo_modal-ModalBoxCloseButton')


class RecommendationWidget(GenericLocatorWidget):
    """The widget representation of recommendation item."""

    EXPAND_BUTTON = ".//div[contains(@class, 'expand')]"
    NAME = ".//div/p[contains(@class, 'item-heading')]"
    RISK_LABEL = ".//div/span[contains(@class, 'risk-label')]"
    TEXT = ".//div[contains(@class, 'list-group-item-container')]"

    @property
    def expand_button(self):
        """Return the expand button element."""
        return self.browser.element(self.EXPAND_BUTTON, parent=self)

    @property
    def expanded(self):
        """Check whether this recommendation is expanded or not."""
        return 'active' in self.browser.get_attribute('class', self.expand_button)

    def expand(self):
        """Expand the recommendation item section."""
        if not self.expanded:
            self.browser.click(self.EXPAND_BUTTON, parent=self)

    @property
    def name(self):
        """Return the name displayed for this recommendation item"""
        return self.browser.text(self.NAME, parent=self)

    @property
    def label(self):
        """Return the risk label displayed for this recommendation item"""
        return self.browser.text(self.RISK_LABEL, parent=self)

    @property
    def text(self):
        """Return the text displayed for this recommendation item"""
        return self.browser.text(self.TEXT, parent=self)

    def read(self):
        if self.expanded:
            return {'name': self.name, 'label': self.label, 'text': self.text}
        else:
            self.expand()
            return {'name': self.name, 'label': self.label, 'text': self.text}


class RecommendationListView(View):
    """Insights tab view of a host"""

    ROOT = "//div[contains(@id, 'host_details_insights_tab')]"
    ITEMS = ".//div[@id='hits_list']/div[contains(@class, 'list-group-item')]"
    ITEM_WIDGET = RecommendationWidget

    def items(self):
        items = []
        for index, _ in enumerate(self.browser.elements(self.ITEMS, parent=self)):
            item = self.ITEM_WIDGET(self, f'{self.ITEMS}[{index + 1}]')
            items.append(item)
        return items

    def read(self):
        return [item.read() for item in self.items()]


class HostDetailsView(BaseLoggedInView):
    breadcrumb = PF4BreadCrumb('breadcrumbs-list')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'All Hosts'
            and self.breadcrumb.read() != 'Create Host'
        )

    boot_disk = ActionsDropdown(
        "//div[contains(@class, 'btn-group')][contains(., 'Boot')][not(*[self::div])]"
    )
    schedule_remote_job = ActionsDropdown(
        "//div[contains(@class, 'btn-group')][contains(., 'Schedule')][not(*[self::div])]"
    )
    back = Text("//a[normalize-space(.)='Back']")
    webconsole = Text("//a[normalize-space(.)='Web Console']")
    edit = Text("//a[@id='edit-button']")
    clone = Text("//a[@id='clone-button']")
    build = Text("//a[@id='build-review']")
    delete = Text("//a[@id='delete-button']")
    audits_details = Text("//a[normalize-space(.)='Audits']")
    facts_details = Text("//a[normalize-space(.)='Facts']")
    yaml_dump = Text("//a[normalize-space(.)='Puppet YAML']")
    yaml_output = Text('//pre')
    content_details = Text("//a[normalize-space(.)='Content']")
    recommendations = Text("//a[normalize-space(.)='Recommendations']")

    @View.nested
    class properties(SatTab):
        properties_table = SatTableWithUnevenStructure(locator="//table[@id='properties_table']")

    @View.nested
    class insights(SatTab):
        insights_tab = RecommendationListView()


class HostEditView(HostCreateView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    toggle_manage = Text("//a[contains(@href, '/toggle_manage')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
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
        return self.browser.wait_for_element(self.title, exception=False) is not None


class HostsChangeGroup(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Change Group - The following hosts are about to be changed']"
    )
    host_group = Select(id='hostgroup_id')


class HostsChangeContentSourceView(View):
    title = Text('//h5')

    hosts_to_update = Text('//span[@class="pf-v5-c-label pf-m-green"]//a')
    ignored_hosts = Text('//span[@class="pf-v5-c-label pf-m-orange"]//a')

    content_source_select = PF5OUIASelect('content-source-select')
    disabled_environment_status = Text('//div[@aria-label="Info Alert"]')

    lce_env_title = Text('//div[normalize-space(.)="Lifecycle environment"]')
    lce_env_path_list = Text('//div[@class="env-path"]/div/div')

    content_view_select = PF5OUIASelect('SelectContentView')
    content_view_select_btn = Text(locator='//button[@aria-label="Options menu" and @tabindex]')

    run_job_invocation = Text(locator='//*[normalize-space(.)="Run job invocation"]')
    update_hosts_manualy = Text(locator='//*[normalize-space(.)="Update hosts manually"]')

    show_more_change_content_source = Text('//button[normalize-space(.)="Show more"]')
    show_less_change_content_source = Text('//button[normalize-space(.)="Show less"]')
    generated_script = Text('//code')


class HostsChangeEnvironment(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Change Environment - "
        "The following hosts are about to be changed']"
    )
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
    fail_on_mismatch = Text("//input[contains(@id, 'optimistic_import_no')]")
    buttons_text = {
        'fix_mismatch': 'Fix {taxonomy} on Mismatch',
        'fail_on_mismatch': 'Fail on Mismatch',
    }

    def __init__(self, parent, **kwargs):
        self.taxonomy = kwargs.pop('taxonomy')
        super().__init__(parent, "//div[@class='modal-body']//div[@id='content']//form", **kwargs)

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
            _text = text.replace('{taxonomy}', self.taxonomy)
            widget = getattr(self, name)
            if _text == value and not self._is_checked(widget):
                widget.click()

    @property
    def is_displayed(self):
        return self.fix_mismatch.is_displayed and self.fail_on_mismatch.is_displayed


class HostsAssignOrganization(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Assign Organization - "
        "The following hosts are about to be changed']"
    )
    organization = Select(id='organization_id')
    on_mismatch = HostsTaxonomyMismatchRadioGroup(taxonomy='Organization')


class HostsAssignLocation(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Assign Location - The following hosts are about to be changed']"
    )
    location = Select(id='location_id')
    on_mismatch = HostsTaxonomyMismatchRadioGroup(taxonomy='Location')


class HostsAssignCompliancePolicy(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Assign Compliance Policy - "
        "The following hosts are about to be changed']"
    )
    policy = Select(id='policy_id')


class HostsUnassignCompliancePolicy(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Unassign Compliance Policy"
        " - The following hosts are about to be changed']"
    )
    policy = Select(id='policy_id')


class HostsChangeOpenscapCapsule(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Change OpenSCAP Capsule - "
        "The following hosts are about to be changed']"
    )
    policy = Select(id='smart_proxy_id')


class HostsDeleteActionDialog(HostsActionCommonDialog):
    title = Text(
        "//h4[normalize-space(.)='Delete Hosts - The following hosts are about to be changed']"
    )


class ChangeContentSourceView(View):
    """Hosts Change Content Source View"""


class HostsDeleteTaskDetailsView(TaskDetailsView):
    """Hosts Delete Task Details View"""


class HostsJobInvocationCreateView(JobInvocationCreateView):
    """Hosts Job Invocation Create View"""


class HostsJobInvocationStatusView(JobInvocationStatusView):
    """Hosts Job Invocation Status View"""
