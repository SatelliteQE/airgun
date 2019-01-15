import re

from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    Select,
    Text,
    TextInput,
    View,
    Table,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
    SatTab,
)
from airgun.views.host import HostCreateView
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    GenericLocatorWidget,
    MultiSelect,
    RadioGroup,
    SatTable,
)


class ComputeResourcesView(BaseLoggedInView, SearchableViewMixin):

    title = Text("//h1[text()='Compute Resources']")
    new = Text("//a[contains(@href, '/compute_resources/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ResourceProviderCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='compute_resource_name')
    description = TextInput(id='compute_resource_description')
    submit = Text('//input[@name="commit"]')

    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    provider_content = ConditionalSwitchableView(reference='provider')

    @provider_content.register('Docker')
    class DockerProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        email = TextInput(id='compute_resource_email')

    @provider_content.register('EC2')
    class EC2ProviderForm(View):
        http_proxy = TextInput(id='compute_resource_http_proxy_id')
        access_key = TextInput(id='compute_resource_user')
        secret_key = TextInput(id='compute_resource_password')

        @View.nested
        class region(View):
            load_regions = Text(
                "//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='s2id_compute_resource_region')

            def before_fill(self, values=None):
                self.load_regions.click()

    @provider_content.register('Google')
    class GCEProviderForm(View):
        google_project_id = TextInput(id='compute_resource_project')
        client_email = TextInput(id='compute_resource_email')
        certificate_path = TextInput(id='compute_resource_key_path')
        load_zones = Text("//*[contains(@id,'test_connection_button')]")

    @provider_content.register('Libvirt')
    class LibvirtProviderForm(View):
        url = TextInput(id='compute_resource_url')
        display_type = Select(id='compute_resource_display_type')
        console_passwords = Checkbox(
            id='compute_resource_set_console_password')

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
        vnc_console_passwords = Checkbox(
            id='compute_resource_set_console_password')
        enable_caching = Checkbox(id='compute_resource_caching_enabled')

        @View.nested
        class datacenter(View):
            load_datacenters = Text("//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='s2id_compute_resource_datacenter')

            def before_fill(self, values=None):
                self.load_datacenters.click()

    @provider_content.register('RHV')
    class RHVProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        api4 = Checkbox(id='compute_resource_use_v4')
        certification_authorities = TextInput(id='compute_resource_public_key')

        @View.nested
        class datacenter(View):
            load_datacenters = Text(
                "//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='s2id_compute_resource_uuid')

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
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Compute Resources'
                and self.breadcrumb.read() == 'Create Compute Resource'
        )


class ResourceProviderEditView(ResourceProviderCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ResourceProviderDetailView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    create_image = Text("//a[contains(@data-id, 'images_new')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute Resources'
            and self.breadcrumb.read() != 'Create Compute Resource'
        )

    @View.nested
    class compute_resource(SatTab):
        TAB_NAME = 'Compute Resource'
        table = SatTable('.//table')

    @View.nested
    class virtual_machines(SatTab, SearchableViewMixin):
        TAB_NAME = 'Virtual Machines'

        actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
        table = Table(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Actions': Text('.//a[@data-method="put"]'),
                'Power': Text('.//span[contains(@class,"label")]'),
            }
        )

    @View.nested
    class compute_profiles(SatTab):
        TAB_NAME = 'Compute profiles'
        table = SatTable(
            './/table',
            column_widgets={
                'Compute profile': Text('./a'),
            }
        )

    @View.nested
    class images(SatTab, SearchableViewMixin):
        table = Table(
            './/table',
            column_widgets={
                'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
            }
        )

    @View.nested
    class containers(SatTab, SearchableViewMixin):
        table = Table(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Action': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
            }
        )


class RemovableWidgetsItemsListView(View):
    """A host for widgets list. Items that can added and removed, mainly used in profile for
    network interfaces and storage.

    Usage::

        @View.nested
        class resources(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='storage_volumes']"
            ITEMS = "./div/div[contains(@class, 'removable-item')]"
            ITEM_WIDGET_CLASS = ComputeResourceRHVProfileStorageItem
    """
    ITEMS = "./div[contains(@class, 'removable-item')]"
    ITEM_WIDGET_CLASS = None
    ITEM_REMOVE_BUTTON_ATTR = 'remove_button'
    add_item_button = Text(".//a[contains(@class, 'add_nested_fields')]")

    def _get_item_locator(self, index):
        """Return the item locator located at index position"""
        return '{0}[{1}]'.format(self.ITEMS, index + 1)

    def get_item_at_index(self, index):
        """Return the item widget instance at index"""
        return self.ITEM_WIDGET_CLASS(self, self._get_item_locator(index))

    def add_item(self):
        """Add an item by pressing the add_item button and return the item instance"""
        self.add_item_button.click()
        return self.get_item_at_index(self.items_length - 1)

    def remove_item(self, item):
        """Remove item widget by clicking on it's remove button"""
        if self.ITEM_REMOVE_BUTTON_ATTR:
            getattr(item, self.ITEM_REMOVE_BUTTON_ATTR).click()

    def remove_item_at_index(self, index):
        """Remove item at index"""
        self.remove_item(self.get_item_at_index(index))

    @property
    def items_length(self):
        # Returns the items length
        return len(self.browser.elements(self.ITEMS, parent=self))

    @property
    def items(self):
        """Return all the items widget instances"""
        return [self.get_item_at_index(index) for index in range(self.items_length)]

    def clear(self):
        """Remove all items if item remove button attribute defined."""
        if self.ITEM_REMOVE_BUTTON_ATTR:
            for item in reversed(self.items):
                self.remove_item(item)

    def read(self):
        """Read all items"""
        return [item.read() for item in self.items]

    def fill(self, values):
        """Fill all items.
        :param values: A list of values to fill the item widgets with.
        """
        if not values:
            values = []
        # Clear all before fill
        self.clear()
        for value in values:
            item = self.add_item()
            item.fill(value)


class GenericRemovableWidgetItem(GenericLocatorWidget):
    """Generic Item widget (to be inherited) to be used as Widget Item for
    `RemovableWidgetsItemsListView`.
     """
    remove_button = Text(".//div[@class='remove-button']/a")

    def read(self):
        values = {}
        for widget_name in self.widget_names:
            widget = getattr(self, widget_name)
            try:
                value = widget.read()
            except NoSuchElementException:
                continue
            values[widget_name] = value
        return values

    def fill(self, values):
        if values:
            for key, value in values.items():
                widget = getattr(self, key)
                if widget:
                    widget.fill(value)


class ComputeResourceRHVProfileNetworkItem(GenericRemovableWidgetItem):
    """Compute Resource profile "Network interface" item widget"""
    name = TextInput(locator=".//input[contains(@id, 'name')]")
    network = FilteredDropdown(id="network")
    interface_type = FilteredDropdown(id="interface")


class ComputeResourceRHVProfileStorageItem(GenericRemovableWidgetItem):
    """Compute Resource profile "Storage" item widget"""
    size = TextInput(locator=".//input[contains(@id, 'size_gb')]")
    storage_domain = FilteredDropdown(id="storage_domain")
    preallocate_disk = Checkbox(locator=".//input[contains(@id, 'preallocate')]")
    wipe_disk_after_delete = Checkbox(locator=".//input[contains(@id, 'wipe_after_delete')]")
    disk_interface = FilteredDropdown(id="interface")

    @View.nested
    class bootable(View):
        ROOT = ".//input[contains(@id, 'bootable')]"

        def _is_checked(self):
            return self.browser.get_attribute('checked', self)

        def read(self):
            return self.browser.is_selected(self)

        def fill(self, value):
            if value is True and not self.browser.is_selected(self):
                self.browser.click(self)


class ComputeResourceVMwareProfileNetworkItem(GenericRemovableWidgetItem):
    """VMware Compute Resource Profile "Network interface" item widget"""
    nic_type = FilteredDropdown(id="type")
    network = FilteredDropdown(id="network")


class ComputeResourceVMwareProfileControllerVolumeItem(GenericRemovableWidgetItem):
    """VMware Compute Resource Profile "Storage Controller Volume" item widget"""

    storage_pod = FilteredDropdown(
        locator=".//div[label[contains(., 'Storage Pod')]]//div[contains(@class, 'form-control')]")
    data_store = FilteredDropdown(
        locator=".//div[label[contains(., 'Data store')]]//div[contains(@class, 'form-control')]")
    disk_mode = FilteredDropdown(
        locator=".//div[label[contains(., 'Disk Mode')]]//div[contains(@class, 'form-control')]")
    size = TextInput(locator=".//div[label[contains(., 'Size')]]/div/span/input")
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
        locator=".//div[@class='controller-header']//div[contains(@class, 'form-control')]")
    remove_button = Text(".//button[contains(@class, 'remove-controller')]")
    disks = ComputeResourceVMwareProfileControllerVolumeList()


class ResourceProviderProfileView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    compute_profile = FilteredDropdown(id='s2id_compute_attribute_compute_profile_id')
    compute_resource = FilteredDropdown(id='s2id_compute_attribute_compute_resource_id')

    provider_content = ConditionalSwitchableView(reference='current_provider')

    submit = Text('//input[@name="commit"]')

    @property
    def current_provider(self):
        """Retrieve the provider name from the compute resource name.

        Note: The provider name is always appended to the end of the compute resource name,
        for example: compute resource name "foo"

        1. For RHV provider, the compute resource name will be displayed as: "foo (RHV)"
        2. For EC2 provider, the compute resource name will be displayed as:
            "foo (ca-central-1-EC2)" where "ca-central-1" is the region.
        """
        compute_resource_name = self.compute_resource.read()
        return re.findall(r'.*\((?:.*-)*(.*?)\)\Z|$', compute_resource_name)[0]

    @provider_content.register('EC2')
    class EC2ResourceForm(View):
        flavor = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_flavor_id')
        image = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_image_id')
        availability_zone = FilteredDropdown(
            id='s2id_compute_attribute_vm_attrs_availability_zone')
        subnet = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_subnet_id')
        security_groups = MultiSelect(id='ms-compute_attribute_vm_attrs_security_group_ids')
        managed_ip = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_managed_ip')

    @provider_content.register('RHV')
    class RHVResourceForm(View):
        cluster = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_cluster')
        template = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_template')
        instance_type = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_instance_type')
        cores = TextInput(id='compute_attribute_vm_attrs_cores')
        sockets = TextInput(id='compute_attribute_vm_attrs_sockets')
        memory = TextInput(id='compute_attribute_vm_attrs_memory')
        highly_available = Checkbox(id='compute_attribute_vm_attrs_ha')

        @View.nested
        class network_interfaces(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='network_interfaces']"
            ITEM_WIDGET_CLASS = ComputeResourceRHVProfileNetworkItem

        @View.nested
        class storage(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='storage_volumes']"
            ITEMS = "./div/div[contains(@class, 'removable-item')]"
            ITEM_WIDGET_CLASS = ComputeResourceRHVProfileStorageItem

    @provider_content.register('VMware')
    class VMwareResourceForm(View):
        cpus = TextInput(id='compute_attribute_vm_attrs_cpus')
        cores_per_socket = TextInput(id='compute_attribute_vm_attrs_corespersocket')
        memory = TextInput(id='compute_attribute_vm_attrs_memory_mb')
        firmware = RadioGroup(
            "//div[label[input[contains(@id, 'compute_attribute_vm_attrs_firmware')]]]")
        cluster = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_cluster')
        resource_pool = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_resource_pool')
        folder = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_path')
        guest_os = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_guest_id')
        virtual_hw_version = FilteredDropdown(
            id='s2id_compute_attribute_vm_attrs_hardware_version')
        memory_hot_add = Checkbox(id='compute_attribute_vm_attrs_memoryHotAddEnabled')
        cpu_hot_add = Checkbox(id='compute_attribute_vm_attrs_cpuHotAddEnabled')
        cdrom_drive = Checkbox(id='compute_attribute_vm_attrs_add_cdrom')
        annotation_notes = TextInput(id='compute_attribute_vm_attrs_annotation')
        image = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_image_id')

        @View.nested
        class network_interfaces(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='network_interfaces']"
            ITEM_WIDGET_CLASS = ComputeResourceVMwareProfileNetworkItem

        @View.nested
        class storage(RemovableWidgetsItemsListView):
            ROOT = "//div[@id='scsi_controllers']"
            ITEMS = ".//div[@class='controller-container']"
            ITEM_WIDGET_CLASS = ComputeResourceVMwareProfileStorageItem
            add_item_button = Text(".//button[contains(@class, 'add-controller')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10)
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
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
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
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10)
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
            self.breadcrumb, exception=False, ensure_page_safe=True, timeout=10)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Compute Resources'
                and self.breadcrumb.locations[2] == 'Images'
                and self.breadcrumb.read().startswith('Edit ')
        )


class ComputeResourceRHVImageCreateView(ComputeResourceGenericImageCreateView):
    """RHV Compute resource Image create view."""


class ComputeResourceRHVImageEditView(
        ComputeResourceRHVImageCreateView, ComputeResourceGenericImageEditViewMixin):
    """RHV Compute resource Image edit view."""


class ComputeResourceVMwareImageCreateView(ComputeResourceGenericImageCreateView):
    """VMWare ComputeResource Image create View"""


class ComputeResourceVMwareImageEditView(
        ComputeResourceVMwareImageCreateView, ComputeResourceGenericImageEditViewMixin):
    """VMWare ComputeResource Image edit View"""
