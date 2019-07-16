from widgetastic_patternfly import BreadCrumb

from widgetastic.widget import (
    Checkbox,
    GenericLocatorWidget,
    ConditionalSwitchableView,
    Table,
    Text,
    TextInput,
    View,
    Widget,
)
from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
    SatTab,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
)


class StatusIcon(GenericLocatorWidget):
    """The status for virtwho configure can be: green, gray.

    green: The virt-who report has not arrived within the interval,
         which indicates there was no change on hypervisor
    gray: The configuration was not deployed yet or the virt-who was
        unable to report the status
    """

    def __init__(self, parent, locator=None, logger=None):
        """Provide default locator value if it wasn't passed"""
        if not locator:
            locator = ".//span[contains(@class, 'virt-who-config-report-status')]"
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def color(self):
        """Returns string representing icon color: 'gray', 'green' or'unknown'.
        rgba is created for chrome.
        rbg is created for firefox.
        """
        colors = {
            'rgba(54, 54, 54, 1)': 'gray',
            'rgba(63, 156, 53, 1)': 'green',
            'rgb(63, 156, 53)': 'green',
            'rgb(54, 54, 54)': 'gray',
        }
        return colors.get(
            self.browser.element(self, parent=self.parent).value_of_css_property('color'),
            'unknown'
        )

    def read(self):
        """Returns current icon color"""
        return self.color


class VirtwhoConfiguresView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Virt-who Configurations']")
    new = Text("//a[contains(@href, '/foreman_virt_who_configure/configs/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Status': StatusIcon(),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class VirtwhoConfigureCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='foreman_virt_who_configure_config_name')
    interval = FilteredDropdown(id='foreman_virt_who_configure_config_interval')
    satellite_url = TextInput(id='foreman_virt_who_configure_config_satellite_url')
    hypervisor_id = FilteredDropdown(id='foreman_virt_who_configure_config_hypervisor_id')
    debug = Checkbox(id='foreman_virt_who_configure_config_debug')
    proxy = TextInput(id='foreman_virt_who_configure_config_proxy')
    no_proxy = TextInput(id='foreman_virt_who_configure_config_no_proxy')
    filtering = FilteredDropdown(id='foreman_virt_who_configure_config_listing_mode')
    filtering_content = ConditionalSwitchableView(reference='filtering')
    hypervisor_type = FilteredDropdown(id='foreman_virt_who_configure_config_hypervisor_type')
    hypervisor_content = ConditionalSwitchableView(reference='hypervisor_type')
    submit = Text('//input[@name="commit"]')

    @hypervisor_content.register(
        lambda hypervisor_type: hypervisor_type.endswith(
            ('(esx)', '(rhevm)', '(hyperv)', '(xen)')
        )
    )
    class HypervisorForm(View):
        server = TextInput(id='foreman_virt_who_configure_config_hypervisor_server')
        username = TextInput(id='foreman_virt_who_configure_config_hypervisor_username')
        password = TextInput(id='foreman_virt_who_configure_config_hypervisor_password')

    @hypervisor_content.register('libvirt')
    class LibvirtForm(View):
        server = TextInput(id='foreman_virt_who_configure_config_hypervisor_server')
        username = TextInput(id='foreman_virt_who_configure_config_hypervisor_username')

    @hypervisor_content.register('Container-native virtualization')
    class KubevirtForm(View):
        server = TextInput(id='foreman_virt_who_configure_config_hypervisor_server')
        kubeconfig = TextInput(id='foreman_virt_who_configure_config_kubeconfig_path')

    @filtering_content.register('Unlimited', default=True)
    class FilterUnlimitedForm(View):
        pass

    @filtering_content.register('Whitelist')
    class FilterWhitelistForm(View):
        filter_hosts = TextInput(
            id='foreman_virt_who_configure_config_whitelist'
        )
        filter_host_parents = TextInput(
            id='foreman_virt_who_configure_config_filter_host_parents'
        )

    @filtering_content.register('Blacklist')
    class FilterBlacklistForm(View):
        exclude_hosts = TextInput(
            id='foreman_virt_who_configure_config_blacklist'
        )
        exclude_host_parents = TextInput(
            id='foreman_virt_who_configure_config_exclude_host_parents'
        )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Satellite Virt Who Configure Configs'
            and self.breadcrumb.read() == 'New Virt-who Config'
        )


class VirtwhoConfigureEditView(VirtwhoConfigureCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Configurations'
            and self.breadcrumb.read().startswith('Edit ')
        )


class VirtwhoConfigureDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    edit = Text("//a[text()='Edit']")
    delete = Text("//a[text()='Delete']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Configurations'
                and self.breadcrumb.read() != 'Create Config'
        )

    @View.nested
    class overview(SatTab):
        status = StatusIcon()
        hypervisor_type = Text('.//span[contains(@class,"config-hypervisor_type")]')
        hypervisor_server = Text('.//span[contains(@class,"config-hypervisor_server")]')
        hypervisor_username = Text('.//span[contains(@class,"config-hypervisor_username")]')
        interval = Text('.//span[contains(@class,"config-interval")]')
        satellite_url = Text('.//span[contains(@class,"config-satellite_url")]')
        hypervisor_id = Text('.//span[contains(@class,"config-hypervisor_id")]')
        filtering = Text('.//span[contains(@class,"config-listing_mode")]')
        debug = Text('.//span[contains(@class,"config-debug")]')

    @View.nested
    class deploy(SatTab):
        command = Text("//pre[@id='config_command']")
        script = Text("//pre[@id='config_script']")
