import re

from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Table,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
    SearchableViewMixinPF4,
)
from airgun.views.host import HostCreateView
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    MultiSelect,
    RadioGroup,
    RemovableWidgetsItemsListView,
    SatTable,
)


class ComputeResourcesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('//*[(self::h1 or self::h5) and normalize-space(.)="Compute Resources"]')
    new = Text('//a[normalize-space(.)="Create Compute Resource"]')
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ResourceProviderCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='compute_resource_name')
    description = TextInput(id='compute_resource_description')
    submit = Text('//input[@name="commit"]')

    provider = FilteredDropdown(id='compute_resource_provider')
    provider_content = ConditionalSwitchableView(reference='provider')

    @provider_content.register('EC2')
    class EC2ProviderForm(View):
        access_key = TextInput(id='compute_resource_user')
        secret_key = TextInput(id='compute_resource_password')

        @View.nested
        class region(View):
            load_regions = Text("//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='compute_resource_region')

            def before_fill(self, values=None):
                self.load_regions.click()

        @View.nested
        class http_proxy(View):
            value = FilteredDropdown(id='compute_resource_http_proxy_id')

    @provider_content.register('Google')
    class GCEProviderForm(View):
        json_key = TextInput(id='gce_json')
        upload_button = Text("//input[@id='password_json']")

        @View.nested
        class zone(View):
            load_zones = Text("//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='compute_resource_zone')

            def before_fill(self, values=None):
                self.load_zones.click()

        @View.nested
        class http_proxy(View):
            value = FilteredDropdown(id='compute_resource_http_proxy_id')

    @provider_content.register('Libvirt')
    class LibvirtProviderForm(View):
        url = TextInput(id='compute_resource_url')
        display_type = Select(id='compute_resource_display_type')
        console_passwords = Checkbox(id='compute_resource_set_console_password')

    @provider_content.register('RHEL OpenStack Platform')
    class OpenStackProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        domain = TextInput(id='compute_resource_domain')

    @provider_content.register('Rackspace')
    class RackspaceProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        api_key = TextInput(id='compute_resource_password')
        region = Select(id='compute_resource_region')

    @provider_content.register('VMware')
    class VMwareProviderForm(View):
        vcenter = TextInput(id='compute_resource_server')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        display_type = Select(id='compute_resource_display_type')
        vnc_console_passwords = Checkbox(id='compute_resource_set_console_password')
        enable_caching = Checkbox(id='compute_resource_caching_enabled')

        @View.nested
        class datacenter(View):
            load_datacenters = Text("//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='compute_resource_datacenter')

            def before_fill(self, values=None):
                self.load_datacenters.click()

    @View.nested
    class compute_resource(SatTab):
        TAB_NAME = 'Compute Resource'

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-compute_resource_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-compute_resource_organization_ids')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.read() == 'Create Compute Resource'
        )


class ResourceProviderEditView(ResourceProviderCreateView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ResourceProviderDetailView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    create_image = Text("//a[contains(@class,'btn-primary')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.read() != 'Create Compute Resource'
        )

    @View.nested
    class compute_resource(SatTab):
        TAB_NAME = 'Compute Resource'
        ROOT = ".//div[@id='primary']"

        table = SatTable('.//table')

    @View.nested
    class virtual_machines(SatTab, SearchableViewMixin):
        TAB_NAME = 'Virtual Machines'
        ROOT = ".//div[@id='vms']"

        actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
        table = Table(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Actions': Text('.//a[@data-method="put"]'),
                'Power': Text('.//span[contains(@class,"label")]'),
            },
        )
        search = TextInput(locator=".//input[contains(@aria-controls, 'DataTables_Table')]")

    @View.nested
    class compute_profiles(SatTab):
        TAB_NAME = 'Compute profiles'
        ROOT = ".//div[@id='compute_profiles']"

        table = SatTable(
            './/table',
            column_widgets={
                'Compute profile': Text('.//a'),
            },
        )

    @View.nested
    class images(SatTab):
        TAB_NAME = 'Images'
        ROOT = ".//div[@id='images']"

        filterbox = TextInput(locator=(".//input[contains(@placeholder, 'Filter')]"))
        table = Table(
            './/table',
            column_widgets={
                'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
            },
        )


class ComputeResourceLibvirtProfileNetworkItem(GenericRemovableWidgetItem):
    """Libvirt Compute Resource Profile "Network interface" item widget"""

    network_type = FilteredDropdown(id="type")
    network = FilteredDropdown(id="bridge")
    nic_type = FilteredDropdown(id="model")


class ComputeResourceLibvirtProfileStorageItem(GenericRemovableWidgetItem):
    """Libvirt Compute Resource profile "Storage" item widget"""

    storage_pool = FilteredDropdown(id="pool_name")
    size = TextInput(locator=".//input[contains(@id, 'capacity')]")
    storage_type = FilteredDropdown(id="format_type")


class ComputeResourceVMwareProfileNetworkItem(GenericRemovableWidgetItem):
    """VMware Compute Resource Profile "Network interface" item widget"""

    nic_type = FilteredDropdown(id="type")
    network = FilteredDropdown(id="network")


class ComputeResourceVMwareProfileControllerVolumeItem(GenericRemovableWidgetItem):
    """VMware Compute Resource Profile "Storage Controller Volume" item widget"""

    storage_pod = FilteredDropdown(
        locator=".//div[label[contains(., 'Storage Pod')]]//select[contains(@class, 'form-control')]"
    )
    data_store = FilteredDropdown(
        locator=".//div[label[contains(., 'Data store')]]//select[contains(@class, 'form-control')]"
    )
    disk_mode = FilteredDropdown(
        locator=".//div[label[contains(., 'Disk Mode')]]//select[contains(@class, 'form-control')]"
    )
    size = TextInput(locator=".//div[label[contains(., 'Size')]]//input")
    thin_provision = Checkbox(locator=".//div[label[contains(., 'Thin provision')]]/div/input")
    eager_zero = Checkbox(locator=".//div[label[contains(., 'Eager zero')]]/div/input")

    remove_button = Text(".//button[contains(@class, 'close')]")


class ComputeResourceVMwareProfileControllerVolumeList(RemovableWidgetsItemsListView):
    """VMware Compute Resource Profile SCSI Controller Volumes List"""

    ROOT = "."
    ITEMS = ".//div[@class='disk-container']"
    ITEM_WIDGET_CLASS = ComputeResourceVMwareProfileControllerVolumeItem
    add_item_button = Text(".//button[contains(@class, 'add-disk')]")


class ComputeResourceVMwareProfileStorageItem(GenericRemovableWidgetItem):
    """VMware  Compute Resource Profile Storage Controller item widget"""

    controller = FilteredDropdown(
        locator=".//div[@class='controller-header']//select[contains(@class, 'form-control')]"
    )
    remove_button = Text(".//button[contains(concat(' ', @class, ' '), ' btn-remove-controller ')]")
    disks = ComputeResourceVMwareProfileControllerVolumeList()


class ResourceProviderProfileView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    compute_profile = FilteredDropdown(id='compute_attribute_compute_profile_id')
    compute_resource = FilteredDropdown(id='compute_attribute_compute_resource_id')

    provider_content = ConditionalSwitchableView(reference='current_provider')

    submit = Text('//input[@name="commit"]')

    @property
    def current_provider(self):
        """Retrieve the provider name from the compute resource name.

        Note: The provider name is always appended to the end of the compute resource name,
        for example: compute resource name "foo"

        1. For EC2 provider, the compute resource name will be displayed as:
            "foo (ca-central-1-EC2)" where "ca-central-1" is the region.
        """
        compute_resource_name = self.compute_resource.read()
        return re.findall(r'.*\((?:.*-)*(.*?)\)\Z|$', compute_resource_name)[0]

    @provider_content.register('Libvirt')
    class LibvirtResourceForm(View):
        cpus = TextInput(id='compute_attribute_vm_attrs_cpus')
        memory = TextInput(id='compute_attribute_vm_attrs_memory')
        image = FilteredDropdown(id='compute_attribute_vm_attrs_image_id')

        @View.nested
        class network_interfaces(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='network_interfaces']"
            ITEM_WIDGET_CLASS = ComputeResourceLibvirtProfileNetworkItem

        @View.nested
        class storage(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='storage_volumes']"
            ITEMS = "./div/div[contains(@class, 'removable-item')]"
            ITEM_WIDGET_CLASS = ComputeResourceLibvirtProfileStorageItem

    @provider_content.register('EC2')
    class EC2ResourceForm(View):
        flavor = FilteredDropdown(id='compute_attribute_vm_attrs_flavor_id')
        image = FilteredDropdown(id='compute_attribute_vm_attrs_image_id')
        availability_zone = FilteredDropdown(id='compute_attribute_vm_attrs_availability_zone')
        subnet = FilteredDropdown(id='compute_attribute_vm_attrs_subnet_id')
        security_groups = MultiSelect(id='ms-compute_attribute_vm_attrs_security_group_ids')
        managed_ip = FilteredDropdown(id='compute_attribute_vm_attrs_managed_ip')

    @provider_content.register('Google')
    class GCEResourceForm(View):
        machine_type = FilteredDropdown(id='compute_attribute_vm_attrs_machine_type')
        image = FilteredDropdown(id='compute_attribute_vm_attrs_image_id')
        network = FilteredDropdown(id='compute_attribute_vm_attrs_network')
        external_ip = Checkbox(id='compute_attribute_vm_attrs_associate_external_ip')
        default_disk_size = TextInput(id='compute_attribute_vm_attrs_volumes_attributes_0_size_gb')

    @provider_content.register('VMware')
    class VMwareResourceForm(View):
        cpus = TextInput(id='compute_attribute_vm_attrs_cpus')
        cores_per_socket = TextInput(id='compute_attribute_vm_attrs_corespersocket')
        memory = TextInput(id='compute_attribute_vm_attrs_memory_mb')
        firmware = RadioGroup(
            "//div[label[input[contains(@id, 'compute_attribute_vm_attrs_firmware')]]]"
        )
        cluster = FilteredDropdown(id='compute_attribute_vm_attrs_cluster')
        resource_pool = FilteredDropdown(id='compute_attribute_vm_attrs_resource_pool')
        folder = FilteredDropdown(id='compute_attribute_vm_attrs_path')
        guest_os = FilteredDropdown(id='compute_attribute_vm_attrs_guest_id')
        virtual_hw_version = FilteredDropdown(id='compute_attribute_vm_attrs_hardware_version')
        memory_hot_add = Checkbox(id='compute_attribute_vm_attrs_memoryHotAddEnabled')
        cpu_hot_add = Checkbox(id='compute_attribute_vm_attrs_cpuHotAddEnabled')
        cdrom_drive = Checkbox(id='compute_attribute_vm_attrs_add_cdrom')
        annotation_notes = TextInput(id='compute_attribute_vm_attrs_annotation')
        image = FilteredDropdown(id='compute_attribute_vm_attrs_image_id')

        @View.nested
        class network_interfaces(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='network_interfaces']"
            ITEM_WIDGET_CLASS = ComputeResourceVMwareProfileNetworkItem

            nic_type = FilteredDropdown(id='select2-chosen-9')
            network = FilteredDropdown(id='select2-chosen-10')

        @View.nested
        class storage(RemovableWidgetsItemsListView):
            ROOT = "//div[contains(concat(' ', @class, ' '), ' vmware-storage-container ')]"
            ITEMS = "//div[contains(concat(' ', @class, ' '), ' controller-container ')]"
            ITEM_WIDGET_CLASS = ComputeResourceVMwareProfileStorageItem
            add_item_button = Text(
                "//button[contains(concat(' ', @class, ' '), ' btn-add-controller ')]"
            )
            data_store = FilteredDropdown(
                "//div[@class='select2-container form-control select2-allowclear']/a/span[1]"
            )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10
        )
        if not breadcrumb_loaded:
            return False
        breadcrumb_text = self.breadcrumb.read()
        return (
            self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.locations[2] == 'Compute Profiles'
            and (breadcrumb_text.startswith('Edit ') or breadcrumb_text.startswith('New '))
        )


class ResourceProviderVMImport(HostCreateView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources Vms'
            and self.breadcrumb.read().startswith('Import ')
        )


class ComputeResourceGenericImageCreateView(BaseLoggedInView):
    """A Generic Compute Resource Image create view."""

    breadcrumb = BreadCrumb()
    name = TextInput(id='image_name')
    operating_system = FilteredDropdown(id='image_operatingsystem_id')
    architecture = FilteredDropdown(id='image_architecture_id')
    username = TextInput(id='image_username')
    user_data = Checkbox(id='image_user_data')
    password = TextInput(id='image_password')
    image = FilteredDropdown(id='image_uuid')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10
        )
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.locations[2] == 'Images'
            and self.breadcrumb.read() == 'Create image'
        )


class ComputeResourceGenericImageEditViewMixin:
    """A Generic Mixin Resource Image edit view."""

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10
        )
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.locations[2] == 'Images'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ComputeResourceVMwareImageCreateView(ComputeResourceGenericImageCreateView):
    """VMWare ComputeResource Image create View"""


class ComputeResourceVMwareImageEditView(
    ComputeResourceVMwareImageCreateView, ComputeResourceGenericImageEditViewMixin
):
    """VMWare ComputeResource Image edit View"""
