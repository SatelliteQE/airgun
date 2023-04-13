from navmazing import NavigateToSibling

from airgun.entities.host import HostEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.host_new import AllAssignedRolesView
from airgun.views.host_new import EnableTracerView
from airgun.views.host_new import InstallPackagesView
from airgun.views.host_new import ModuleStreamDialog
from airgun.views.host_new import NewHostDetailsView
from airgun.views.job_invocation import JobInvocationCreateView


class NewHostEntity(HostEntity):
    def create(self, values):
        """Create new host entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        self.browser.click(view.submit, ignore_ajax=True)
        self.browser.plugin.ensure_page_safe(timeout='600s')
        host_view = NewHostDetailsView(self.browser)
        host_view.wait_displayed()
        host_view.flash.assert_no_error()
        host_view.flash.dismiss()

    def get_details(self, entity_name, widget_names=None):
        """Read host values from Host Details page, optionally only the widgets in widget_names
        will be read.
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.read(widget_names=widget_names)

    def schedule_job(self, entity_name, values):
        """Schedule a remote execution on selected host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.schedule_job.fill('Schedule a job')
        view = JobInvocationCreateView(self.browser)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()
        view.fill(values)
        view.submit.click()

    def get_packages(self, entity_name, search=""):
        """Filter installed packages on host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.content.packages.select()
        view.content.packages.searchbar.fill(search)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.packages.table.wait_displayed()
        return view.content.packages.read()

    def install_package(self, entity_name, package):
        """Installs package on host using the installation modal"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.packages.select()
        view.content.packages.dropdown.wait_displayed()
        view.content.packages.dropdown.item_select('Install packages')
        view = InstallPackagesView(self.browser)
        view.wait_displayed()
        view.searchbar.fill(package)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.select_all.click()
        view.install.click()

    def apply_package_action(self, entity_name, package_name, action):
        """Apply `action` to selected package based on the `package_name`"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.packages.searchbar.fill(package_name)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.packages.table.wait_displayed()
        view.content.packages.table[0][5].widget.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_errata_by_type(self, entity_name, type):
        """List errata based on type and return table"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.select()
        view.content.errata.type_filter.fill(type)
        self.browser.plugin.ensure_page_safe()
        view.content.errata.table.wait_displayed()
        return view.read(widget_names="content.errata.table")

    def apply_erratas(self, entity_name, search):
        """Apply errata on selected host based on errata_id"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.searchbar.fill(search)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.errata.select_all.click()
        view.content.errata.apply.fill('Apply')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_module_streams(self, entity_name, search):
        """Filter module streams"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.module_streams.select()
        view.content.module_streams.searchbar.fill(search)
        # wait for filter to apply
        self.browser.wait_for_element(locator='//h4[text()="Loading"]', exception=False)
        view.content.module_streams.table.wait_displayed()
        return view.content.module_streams.table.read()

    def apply_module_streams_action(self, entity_name, module_stream, action):
        """Apply `action` to selected Module stream based on the `module_stream`"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.module_streams.searchbar.fill(module_stream)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.module_streams.table[0][5].widget.item_select(action)
        modal = ModuleStreamDialog(self.browser)
        if modal.is_displayed:
            modal.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_repo_sets(self, entity_name, search):
        """Get all repository sets available for host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.repository_sets.searchbar.fill(search)
        self.browser.plugin.ensure_page_safe()
        return view.content.repository_sets.table.read()

    def override_repo_sets(self, entity_name, repo_set, action):
        """Change override for repository set"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.repository_sets.searchbar.fill(repo_set)
        self.browser.plugin.ensure_page_safe()
        view.content.repository_sets.table[0][5].widget.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_ansible_roles(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.ansible.roles.table.read()

    def get_ansible_roles_modal(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.ansible.roles.assignedRoles.click()
        view = AllAssignedRolesView(self.browser)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.table.read()

    def enable_tracer(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.traces.enable_traces.click()
        modal = EnableTracerView(self.browser)
        if modal.is_displayed:
            modal.confirm.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_tracer(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.traces.read()

    def get_os_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.operating_system.read()

    def get_provisioning_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.provisioning.read()

    def get_bios_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.bios.read()

    def get_registration_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.registration_details.read()

    def get_hw_properties(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.hw_properties.read()

    def get_provisioning_templates(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        d = view.details.read()
        return d['provisioning_templates']['templates_table']

    def get_networking_interfaces(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.networking_interfaces.networking_interfaces_accordion.items()

    def get_networking_interfaces_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        net_devices = [
            i.split()[0]
            for i in view.details.networking_interfaces.networking_interfaces_accordion.items()
        ]

        for dev in net_devices[1:]:
            view.details.networking_interfaces.networking_interfaces_accordion.toggle(dev)

        def dict_val_gen(item_name):
            """Generator needed to fill the networking interface dictionary"""
            locator_templ = (
                './/div[contains(@class, "pf-c-accordion__expanded-content-body")]'
                '//div[.//dt[normalize-space(.)="{}"]]//div'
            )
            values = self.browser.elements(locator_templ.format(item_name))
            yield values

        networking_interface_dict = {}
        tmp = {
            'fqdn': [i.text for i in list(dict_val_gen('FQDN'))[0]],
            'ipv4': [i.text for i in list(dict_val_gen('IPv4'))[0]],
            'ipv6': [i.text for i in list(dict_val_gen('IPv6'))[0]],
            'mac': [i.text for i in list(dict_val_gen('MAC'))[0]],
            # TODO: After RFE BZ2183086 is resolved, uncomment line below
            # 'subnet': [i.text for i in list(dict_val_gen('Subnet'))[0]],
            'mtu': [i.text for i in list(dict_val_gen('MTU'))[0]],
        }

        for i, dev in enumerate(net_devices):
            networking_interface_dict[dev] = {key: tmp[key][i] for key in tmp}

        return networking_interface_dict

    def get_installed_products(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        installed_products_list = view.details.installed_products.read()
        return installed_products_list['installed_products_list']

    def get_parameters(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.parameters.read()

    def add_new_parameter(self, entity_name, parameter_name, parameter_type, parameter_value):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.parameters.add_parameter.click()
        view.parameters.new_parameter_name.fill(parameter_name)
        view.parameters.new_parameter_type.fill(parameter_type)
        view.parameters.new_parameter_value.fill(parameter_value)
        view.parameters.confirm_addition.click()

    def get_traces(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.traces.read()

    def get_puppet_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        reports_table = view.puppet.puppet_reports_table.read()
        x = view.puppet.puppet_details.read()
        x['reports_table'] = reports_table
        return x

    def get_puppet_enc_preview(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.puppet.enc_preview.read()

    def get_reports(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.reports.read()

    def get_insights(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.insights.read()


@navigator.register(NewHostEntity, 'NewDetails')
class ShowNewHostDetails(NavigateStep):
    """Navigate to Host Details page by clicking on necessary host name in the table

    Args:
        entity_name: name of the host
    """

    VIEW = NewHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewHostEntity, 'AnsibleTab')
class ShowNewHostAnsible(NavigateStep):
    """Navigate to the Ansible Tab of Host Details by clicking on the subtab"""

    VIEW = NewHostDetailsView

    prerequisite = NavigateToSibling('NewDetails')

    def step(self, *args, **kwargs):
        print(self.parent.rolesListTable)
