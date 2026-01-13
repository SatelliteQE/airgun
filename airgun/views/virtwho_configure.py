from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    GenericLocatorWidget,
    Table,
    Text,
    TextInput,
    View,
    Widget,
)
from widgetastic_patternfly import BreadCrumb

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import ActionsDropdown, FilteredDropdown


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
        """Detect status from PF5 element attributes.

        PF5 classes: pf-v5-c-icon with status modifier classes
        """
        element = self.browser.element(self.STATUS_ICON)
        attrs = self.browser.get_attribute('class', element)

        # Check for PF5 status patterns
        if 'pf-m-success' in attrs or 'status-ok' in attrs:
            return 'ok'
        elif 'pf-m-info' in attrs or 'status-info' in attrs:
            return 'info'
        elif 'pf-m-warning' in attrs or 'status-warn' in attrs:
            return 'warning'
        elif 'pf-m-danger' in attrs or 'status-error' in attrs:
            return 'error'
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
    """Return the virtwho configure debug status."""

    DEBUG = ".//span[contains(@class,'config-debug')]"
    # PF5 check icons
    STATUS = ".//span[contains(@class,'pf-v5-c-icon') and contains(@class,'pf-m-success')]"

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


class VirtwhoConfiguresAHVDebug(Widget):
    """Return the virtwho configure ahv_internal_debug status."""

    DEBUG = ".//span[contains(@class,'config-ahv_internal_debug')]"
    # PF5 check icons
    STATUS = ".//span[contains(@class,'pf-v5-c-icon') and contains(@class,'pf-m-success')]"

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
        """Returns the ahv_internal_debug status"""
        return self.status

    def fill(self, value):
        raise ReadOnlyWidgetError('ahv_internal_debug status widget is read only')


class VirtwhoConfiguresView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Virt-who Configurations']")
    new = Text("//a[contains(@href, '/foreman_virt_who_configure/configs/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Status': VirtwhoConfigureStatus('.'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class VirtwhoConfigureCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='foreman_virt_who_configure_config_name')
    organization_id = FilteredDropdown(id='foreman_virt_who_configure_config_organization_id')
    interval = FilteredDropdown(id='foreman_virt_who_configure_config_interval')
    satellite_url = TextInput(id='foreman_virt_who_configure_config_satellite_url')
    hypervisor_id = FilteredDropdown(id='foreman_virt_who_configure_config_hypervisor_id')
    debug = Checkbox(id='foreman_virt_who_configure_config_debug')
    proxy = FilteredDropdown(id='foreman_virt_who_configure_config_http_proxy_id')
    no_proxy = TextInput(id='foreman_virt_who_configure_config_no_proxy')
    filtering = FilteredDropdown(id='foreman_virt_who_configure_config_listing_mode')
    filtering_content = ConditionalSwitchableView(reference='filtering')
    hypervisor_type = FilteredDropdown(id='foreman_virt_who_configure_config_hypervisor_type')
    hypervisor_content = ConditionalSwitchableView(reference='hypervisor_type')
    ahv_internal_debug = Checkbox(id='foreman_virt_who_configure_config_ahv_internal_debug')
    submit = Text('//input[@name="commit"]')

    @hypervisor_content.register(
        lambda hypervisor_type: hypervisor_type.endswith(('(esx)', '(hyperv)', '(xen)'))
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

    @hypervisor_content.register('Nutanix AHV (ahv)')
    class NutanixForm(View):
        server = TextInput(id='foreman_virt_who_configure_config_hypervisor_server')
        username = TextInput(id='foreman_virt_who_configure_config_hypervisor_username')
        password = TextInput(id='foreman_virt_who_configure_config_hypervisor_password')
        prism_flavor = FilteredDropdown(id='foreman_virt_who_configure_config_prism_flavor')
        filtering_content = ConditionalSwitchableView(reference='prism_flavor')

    @filtering_content.register('Unlimited', default=True)
    class FilterUnlimitedForm(View):
        pass

    @filtering_content.register('Whitelist')
    class FilterWhitelistForm(View):
        filter_hosts = TextInput(id='foreman_virt_who_configure_config_whitelist')
        filter_host_parents = TextInput(id='foreman_virt_who_configure_config_filter_host_parents')

    @filtering_content.register('Blacklist')
    class FilterBlacklistForm(View):
        exclude_hosts = TextInput(id='foreman_virt_who_configure_config_blacklist')
        exclude_host_parents = TextInput(
            id='foreman_virt_who_configure_config_exclude_host_parents'
        )

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Satellite Virt Who Configure Configs'
            and self.breadcrumb.read() == 'New Virt-who Config'
        )


class VirtwhoConfigureEditView(VirtwhoConfigureCreateView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Virt-who Configurations'
            and self.breadcrumb.read().startswith('Edit ')
        )


class VirtwhoConfigureDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    edit = Text("//a[normalize-space(.)='Edit']")
    delete = Text("//a[normalize-space(.)='Delete']")

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Virt-who Configurations'
            and self.breadcrumb.read() != 'Create Config'
        )

    @View.nested
    class overview(SatTab):
        status = VirtwhoConfigureStatus('.')
        debug = VirtwhoConfiguresDebug()
        ahv_internal_debug = VirtwhoConfiguresAHVDebug()
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
        proxy = Text('.//span[contains(@class,"config-http_proxy_id")]')
        no_proxy = Text('.//span[contains(@class,"config-no_proxy")]')
        kubeconfig_path = Text('.//span[contains(@class,"config-kubeconfig_path")]')
        prism_flavor = Text('.//span[contains(@class,"config-prism_flavor")]')

        _label_locator = "//span[contains(@class, '{class_name}')]/../preceding-sibling::div/strong"
        status_label = Text(_label_locator.format(class_name='config-status'))
        debug_label = Text(_label_locator.format(class_name='config-debug'))
        hypervisor_type_label = Text(_label_locator.format(class_name='config-hypervisor_type'))
        hypervisor_server_label = Text(_label_locator.format(class_name='config-hypervisor_server'))
        hypervisor_username_label = Text(
            _label_locator.format(class_name='config-hypervisor_username')
        )
        interval_label = Text(_label_locator.format(class_name='config-interval'))
        satellite_url_label = Text(_label_locator.format(class_name='config-satellite_url'))
        hypervisor_id_label = Text(_label_locator.format(class_name='config-hypervisor_id'))
        filtering_label = Text(_label_locator.format(class_name='config-listing_mode'))
        filter_hosts_label = Text(_label_locator.format(class_name='config-whitelist'))
        filter_host_parents_label = Text(
            _label_locator.format(class_name='config-filter_host_parents')
        )
        exclude_hosts_label = Text(_label_locator.format(class_name='config-blacklist'))
        exclude_host_parents_label = Text(
            _label_locator.format(class_name='config-exclude_host_parents')
        )
        proxy_label = Text(_label_locator.format(class_name='config-http_proxy_id'))
        no_proxy_label = Text(_label_locator.format(class_name='config-no_proxy'))
        kubeconfig_path_label = Text(_label_locator.format(class_name='config-kubeconfig_path'))
        prism_flavor_label = Text(_label_locator.format(class_name='config-prism_flavor'))

    @View.nested
    class deploy(SatTab):
        command = Text("//pre[@id='config_command']")
        script = VirtwhoConfigureScript()
        download = Text("//a[normalize-space(.)='Download the script']")
