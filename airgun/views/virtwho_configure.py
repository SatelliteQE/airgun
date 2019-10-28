from widgetastic_patternfly import BreadCrumb
from widgetastic.exceptions import NoSuchElementException

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
from airgun.exceptions import ReadOnlyWidgetError


class VirtwhoConfigureStatus(GenericLocatorWidget):
    """The status for virtwho configure can be: ok, info, warning.
    ok: The virt-who report has not arrived within the interval,
         which indicates there was no change on hypervisor
    info: The configuration was not deployed yet or the virt-who was
        unable to report the status
    warning: The configuration is invalid and not available.
    """

    STATUS_ICON = ".//span[contains(@class, 'virt-who-config-report-status')]"

    @property
    def status(self):
        """The attributes for the element is such as:
        virt-who-config-report-status pficon-ok status-ok
        virt-who-config-report-status pficon-info status-info
        """
        element = self.browser.element(self.STATUS_ICON)
        attrs = self.browser.get_attribute('class', element)
        if 'status-ok' in attrs:
            return 'ok'
        elif 'status-info' in attrs:
            return 'info'
        elif 'status-warn' in attrs:
            return 'warning'
        else:
            return 'unknown'

    def read(self):
        """Returns current status"""
        return self.status

    def fill(self, value):
        raise ReadOnlyWidgetError('Status widget is read only')


class VirtwhoConfigureScript(Widget):
    """Return the virtwho configure script by innerHTML.
    It will preserve the line break and whitespace.
    """

    SCRIPT_PRE = ".//pre[@id='config_script']"

    @property
    def content(self):
        element = self.browser.element(self.SCRIPT_PRE)
        return element.get_attribute('innerHTML')

    def read(self):
        """Returns the script content"""
        return self.content

    def fill(self, value):
        raise ReadOnlyWidgetError('Script widget is read only')


class VirtwhoConfiguresDebug(Widget):
    """Return the virtwho configure debug status.
    """

    DEBUG = ".//span[contains(@class,'config-debug')]"
    STATUS = ".//span[contains(@class,'fa-check')]"

    @property
    def status(self):
        debug = self.browser.element(self.DEBUG)
        try:
            self.browser.element(self.STATUS, parent=debug)
            checkbox = True
        except NoSuchElementException:
            checkbox = False
        return checkbox

    def read(self):
        """Returns the debug status"""
        return self.status

    def fill(self, value):
        raise ReadOnlyWidgetError('Debug status widget is read only')


class VirtwhoConfiguresView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Virt-who Configurations']")
    new = Text("//a[contains(@href, '/foreman_virt_who_configure/configs/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Status': VirtwhoConfigureStatus('.'),
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
    class options(View):
        status = Text("//strong[text()='Status']")
        hypervisor_type = Text("//strong[text()='Hypervisor Type']")
        hypervisor_server = Text("//strong[text()='Hypervisor Server']")
        hypervisor_username = Text("//strong[text()='Hypervisor Username']")
        interval = Text("//strong[text()='Interval']")
        satellite_url = Text("//strong[text()='Satellite server FQDN']")
        hypervisor_id = Text("//strong[text()='Hypervisor ID']")
        filtering = Text("//strong[text()='Filtering']")
        filter_hosts = Text("//strong[text()='Filter Hosts']")
        filter_host_parents = Text("//strong[text()='Filter Host Parents']")
        exclude_hosts = Text("//strong[text()='Exclude Hosts']")
        exclude_host_parents = Text("//strong[text()='Exclude Host Parents']")
        debug = Text("//strong[text()='Enable debugging output?']")
        proxy = Text("//strong[text()='HTTP Proxy']")
        no_proxy = Text("//strong[text()='Ignore Proxy']")
        kubeconfig_path = Text("//strong[text()='Kubeconfig Path']")

    @View.nested
    class overview(SatTab):
        status = VirtwhoConfigureStatus('.')
        debug = VirtwhoConfiguresDebug()
        hypervisor_type = Text('.//span[contains(@class,"config-hypervisor_type")]')
        hypervisor_server = Text('.//span[contains(@class,"config-hypervisor_server")]')
        hypervisor_username = Text('.//span[contains(@class,"config-hypervisor_username")]')
        interval = Text('.//span[contains(@class,"config-interval")]')
        satellite_url = Text('.//span[contains(@class,"config-satellite_url")]')
        hypervisor_id = Text('.//span[contains(@class,"config-hypervisor_id")]')
        filtering = Text('.//span[contains(@class,"config-listing_mode")]')
        filter_hosts = Text('.//span[contains(@class,"config-whitelist")]')
        filter_host_parents = Text('.//span[contains(@class,"config-filter_host_parents")]')
        exclude_hosts = Text('.//span[contains(@class,"config-blacklist")]')
        exclude_host_parents = Text('.//span[contains(@class,"config-exclude_host_parents")]')
        proxy = Text('.//span[contains(@class,"config-proxy")]')
        no_proxy = Text('.//span[contains(@class,"config-no_proxy")]')
        kubeconfig_path = Text('.//span[contains(@class,"config-kubeconfig_path")]')

    @View.nested
    class deploy(SatTab):
        command = Text("//pre[@id='config_command']")
        script = VirtwhoConfigureScript()
        download = Text("//a[text()='Download the script']")
