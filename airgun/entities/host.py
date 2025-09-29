from time import sleep

from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.exceptions import DisabledWidgetError
from airgun.helpers.host import HostHelper
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_insights import CloudInsightsView
from airgun.views.host import (
    HostCreateView,
    HostDetailsView,
    HostEditView,
    HostRegisterView,
    HostsAssignCompliancePolicy,
    HostsAssignLocation,
    HostsAssignOrganization,
    HostsChangeContentSourceView,
    HostsChangeEnvironment,
    HostsChangeGroup,
    HostsChangeOpenscapCapsule,
    HostsDeleteActionDialog,
    HostsDeleteTaskDetailsView,
    HostsJobInvocationCreateView,
    HostsJobInvocationStatusView,
    HostStatusesView,
    HostsUnassignCompliancePolicy,
    HostsView,
    RecommendationListView,
    RepositoryListView,
)
from airgun.views.host_new import ManageColumnsView, NewHostDetailsView


class HostEntity(BaseEntity):
    endpoint_path = '/hosts'

    HELPER_CLASS = HostHelper

    def create(self, values):
        """Create new host entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        self.browser.click(view.submit, ignore_ajax=True)
        self.browser.plugin.ensure_page_safe(timeout='800s')
        host_view = NewHostDetailsView(self.browser)
        host_view.wait_displayed()
        host_view.flash.assert_no_error()
        host_view.flash.dismiss()

    def get_register_command(self, values=None, full_read=None):
        """Get curl command generated on Register Host page"""
        view = self.navigate_to(self, 'Register')
        self.browser.plugin.ensure_page_safe()
        if values is not None:
            if ('advanced.repository_gpg_key_url' in values) or ('advanced.repository' in values):
                view.wait_displayed()
                view.advanced.repository_add.click()
                view = RepositoryListView(self.browser)
                if 'advanced.repository' in values:
                    view.repository.fill(values['advanced.repository'])
                if 'advanced.repository_gpg_key_url' in values:
                    view.repository_gpg_key_url.fill(values['advanced.repository_gpg_key_url'])
                view.repository_list_confirm.click()
            view = self.navigate_to(self, 'Register')
            self.browser.plugin.ensure_page_safe()
            view.fill(values)
        if view.general.activation_keys.read():
            self.browser.click(view.generate_command)
            self.browser.plugin.ensure_page_safe()
            view.registration_command.wait_displayed()
        else:
            view.general.new_activation_key_link.wait_displayed()
            if view.generate_command.disabled:
                raise DisabledWidgetError('Generate registration command button is disabled')
        if full_read:
            return view.read()
        return view.registration_command.read()

    def search(self, value):
        """Search for existing host entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_filled_searchbox(self):
        """Read filled searchbox"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.searchbox.read()

    def new_ui_button(self):
        """Click New UI button and return the browser URL"""
        view = self.navigate_to(self, 'All')
        view.new_ui_button.click()
        view.wait_displayed()
        return self.browser.url

    def reset_search(self):
        """This function loads a HostsView and clears the searchbox."""
        view = HostsView(self.browser)
        view.searchbox.clear()

    def host_status(self, value):
        """Get Host status"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        return view.browser.element(view.host_status).get_attribute('data-original-title')

    def get_details(self, entity_name, widget_names=None):
        """Read host values from Host Details page, optionally only the widgets in widget_names
        will be read.
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read(self, entity_name, widget_names=None):
        """Read host values from Host Edit page"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_all(self):
        """Read all values from hosts title page"""
        view = self.navigate_to(self, 'All')
        return view.read()

    def update(self, entity_name, values):
        """Update an existing host with values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name, cancel=False):
        """Delete host from the system"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        wait_for(
            lambda: view.flash.assert_message(
                [f'Success alert: Successfully deleted {entity_name}.']
            ),
            timeout=120,
        )
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read_hosts_after_search(self, entity_name):
        """read_hosts_after_search"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        return view.table.read()

    def delete_interface(self, entity_name, interface_id):
        """Delete host network interface.

        :param entity_name: The host name to delete the network interface from
        :param interface_id: The network interface identifier.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        delete_button = view.interfaces.interfaces_list.row(identifier=interface_id)[
            'Actions'
        ].widget.delete
        if delete_button.disabled:
            raise DisabledWidgetError('Interface Delete button is disabled')
        delete_button.click()
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read_yaml_output(self, entity_name):
        """Get puppet external nodes YAML dump for specific host"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.yaml_dump.click()
        output = view.browser.element(view.yaml_output).text
        view.browser.selenium.back()
        return output

    def read_insights_recommendations(self, entity_name):
        """Get Insights recommendations for host"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.recommendations.click()
        view = self.navigate_to(self, 'Recommendations')
        return view.table.read()

    def insights_tab(self, entity_name):
        """Get details from Insights tab"""
        view = self.navigate_to(self, 'InsightsTab', entity_name=entity_name)
        return view.read()

    def _select_action(self, action_name, entities_list):
        """Navigate to all entities, select the entities, and returns the view
        of the selected action name from main entity select action dropdown.
        """
        return self.navigate_to(
            self, 'Select Action', action_name=action_name, entities_list=entities_list
        )

    def apply_action(self, action_name, entities_list, values=None):
        """Apply action name for host/hosts"""
        if values is None:
            values = {}
        view = self._select_action(action_name, entities_list)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def change_content_source(
        self,
        entities_list,
        content_source,
        lce,
        content_view,
        run_job_invocation=False,
        update_hosts_manually=False,
    ):
        """
        Apply Change Content Source action to one or more hosts

        Args:
            entities_list (list): names of the hosts for which we would like to change the content source
            content_source (str): name of the content source to be selected
            lce (str): name of the LCE to be selected
            content_view (str): name of the content view to be selected
            run_job_invocation (bool): whether to run job invocation in order to change the host's content source
            update_hosts_manually (bool): whether to update hosts manually in order to change the host's content source
        """

        view = self._select_action('Change Content Source', entities_list)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        wait_for(lambda: view.content_source_select.is_displayed, timeout=10, delay=1)
        view.content_source_select.fill(content_source)
        wait_for(lambda: view.lce_env_title.is_displayed, timeout=10, delay=1)
        # click on the specific LCE radio button
        self.browser.click(
            f'//input[@type="radio" and following-sibling::label[normalize-space(.)="{lce}"]]'
        )
        view = HostsChangeContentSourceView(self.browser)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.content_view_select.click()
        wait_for(lambda: view.content_view_select.is_displayed, timeout=10, delay=1)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()

        self.browser.click(f'.//*[contains(text(), "{content_view}")][1]')
        if run_job_invocation:
            view.run_job_invocation.click()
            view.wait_displayed()
            self.browser.plugin.ensure_page_safe(timeout='5s')
        elif update_hosts_manually:
            view.update_hosts_manualy.click()
            view.wait_displayed()
            self.browser.plugin.ensure_page_safe(timeout='5s')

    def change_content_source_get_script(self, entities_list, content_source, lce, content_view):
        """
        Function that reads generated script which is generated while choosing to update hosts manually.
        """

        self.change_content_source(
            entities_list, content_source, lce, content_view, update_hosts_manually=True
        )
        view = HostsChangeContentSourceView(self.browser)
        wait_for(lambda: view.show_more_change_content_source.is_displayed, timeout=10, delay=1)
        view.show_more_change_content_source.click()
        script = view.generated_script.read()
        return script

    def export(self):
        """Export hosts list.

        :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        view.export.click()
        return self.browser.save_downloaded_file()

    def host_statuses(self):
        view = self.navigate_to(self, 'Host Statuses')
        view.wait_displayed()
        statuses = []
        view.status_green_total.wait_displayed()
        statuses.append({'name': 'green_total', 'count': view.status_green_total.read()})
        statuses.append({'name': 'green_owned', 'count': view.status_green_owned.read()})
        statuses.append({'name': 'yellow_total', 'count': view.status_yellow_total.read()})
        statuses.append({'name': 'yellow_owned', 'count': view.status_yellow_owned.read()})
        statuses.append({'name': 'red_total', 'count': view.status_red_total.read()})
        statuses.append({'name': 'red_owned', 'count': view.status_red_owned.read()})
        return statuses

    def schedule_remote_job(self, entities_list, values, timeout=60, wait_for_results=True):
        """Apply Schedule Remote Job action to the hosts names in entities_list

        :param entities_list: The host names to apply the remote job.
        :param values: the values to fill The Job invocation view.
        :param timeout: The time to wait for the job to finish.
        :param wait_for_results: Whether to wait for the job to finish execution.

        :returns: The job invocation status view values
        """
        view = self._select_action('Schedule Remote Job', entities_list)
        view.fill(values)
        sleep(2)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        status_view = HostsJobInvocationStatusView(self.browser)
        sleep(2)
        self.browser.plugin.ensure_page_safe()
        status_view.wait_displayed()
        if wait_for_results:
            status_view.wait_for_result(timeout=timeout)
        return status_view.read()

    def play_ansible_roles(self, entities_list, timeout=60, wait_for_results=True):
        """Play Ansible Roles on hosts names in entities_list
           If keyword 'All' is supplied instead of list, all hosts are selected
           using the checkbox from table header

        :param entities_list: The host names to play the ansible roles on.
        :param timeout: The time to wait for the job to finish.
        :param wait_for_results: Whether to wait for the job to finish execution.

        :returns: The job invocation status view values
        """
        status_view = self._select_action('Run all Ansible roles', entities_list)
        if wait_for_results:
            status_view.wait_for_result(timeout=timeout)
        return status_view.read()

    def delete_hosts(self, entities_list, timeout=60, wait_for_results=True):
        """Delete all hosts from entities list
        If keyword 'All' is supplied instead of list, all hosts are selected
        using the checkbox from table header
        """
        view = self._select_action('Delete Hosts', entities_list)
        sleep(1)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        status_view = HostsDeleteTaskDetailsView(self.browser)
        if wait_for_results:
            status_view.wait_for_result(timeout=timeout)
        return status_view.read()

    def get_puppet_class_parameter_value(self, entity_name, name):
        """Read host Puppet class parameter value.

        :param entity_name: The host name for which to read the parameter.
        :param name: the parameter name.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)  # type: HostEditView
        return view.puppet_enc.puppet_class_parameters.row(name=name)['Value'].widget.read()

    def set_puppet_class_parameter_value(self, entity_name, name, value):
        """Set Puppet class parameter value

        :param str entity_name: The host name for which to set the parameter value.
        :param str name: the parameter name.
        :param dict value: The parameter value
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)  # type: HostEditView
        view.puppet_enc.puppet_class_parameters.row(name=name).fill({'Value': value})
        view.submit.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_webconsole_content(self, entity_name, rhel_version=7):
        """Navigate to host's webconsole and return the hostname from the cockpit page

        :param str entity_name: The host name for which to set the parameter value.
        :param int rhel_version: Choose UI elements based on rhel version.
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.webconsole.click()
        view.validations.assert_no_errors()

        # set locators based on selected UI
        if rhel_version > 7:  # noqa: PLR2004 - Context makes magic number clear
            hostname_element = 'span'
            hostname_id = 'system_information_hostname_text'
        else:
            hostname_element = 'a'
            hostname_id = 'system_information_hostname_button'

        # switch to the last opened tab,
        self.browser.switch_to_window(self.browser.window_handles[-1])
        self.browser.plugin.ensure_page_safe()
        self.browser.wait_for_element(locator='//div[@id="content"]/iframe', exception=True)
        # the remote host content is loaded in an iframe, let's switch to it
        self.browser.switch_to_frame(locator='//div[@id="content"]/iframe')

        self.browser.wait_for_element(
            locator=f'//{hostname_element}[@id="{hostname_id}"]', exception=True, visible=True
        )
        hostname_button = self.browser.selenium.find_elements("id", hostname_id)
        hostname = hostname_button[0].text
        self.browser.switch_to_main_frame()
        self.browser.switch_to_window(self.browser.window_handles[0])
        self.browser.close_window(self.browser.window_handles[-1])
        return hostname

    def manage_table_columns(self, values: dict):
        """
        Select which columns should be displayed in the hosts table.

        :param dict values: items of 'column name: value' pairs
            Example: {'IPv4': True, 'Power': False, 'Model': True}
        """
        view = self.navigate_to(self, 'ManageColumns')
        view.fill(values)
        view.submit()
        self.browser.plugin.ensure_page_safe()
        hosts_view = HostsView(self.browser)
        hosts_view.wait_displayed()

    def get_displayed_table_headers(self):
        """
        Return displayed columns in the hosts table.

        :return list: header names of the hosts table
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        return view.displayed_table_header_names


@navigator.register(HostEntity, 'All')
class ShowAllHosts(NavigateStep):
    """Navigate to All Hosts page"""

    VIEW = HostsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')


@navigator.register(HostEntity, 'New')
class AddNewHost(NavigateStep):
    """Navigate to Create Host page"""

    VIEW = HostCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HostEntity, 'Register')
class RegisterHost(NavigateStep):
    """Navigate to Register Host page"""

    VIEW = HostRegisterView

    prerequisite = NavigateToSibling('All')

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Register Host')


@navigator.register(HostEntity, 'Details')
class ShowHostDetails(NavigateStep):
    """Navigate to Host Details page by clicking on necessary host name in the
    table

    Args:
        entity_name: name of the host
    """

    VIEW = HostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
        host_view = NewHostDetailsView(self.parent.browser)
        host_view.wait_displayed()
        host_view.dropdown.wait_displayed()
        host_view.dropdown.item_select('Legacy UI')


@navigator.register(HostEntity, 'Edit')
class EditHost(NavigateStep):
    """Navigate to Edit Host page by clicking on 'Edit' button for specific
    host in the table

    Args:
        entity_name: name of the host
    """

    VIEW = HostEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Edit')
        self.view.wait_displayed()


@navigator.register(HostEntity, 'Select Action')
class HostsSelectAction(NavigateStep):
    """Navigate to Action page by selecting checkboxes for necessary hosts and
     then clicking on the action name button in 'Select Action' dropdown.

    Args:
        action_name: the action name to select from dropdown button
        entities_list: list of hosts that need to be modified
    """

    ACTIONS_VIEWS = {
        'Change Content Source': HostsChangeContentSourceView,
        'Change Environment': HostsChangeEnvironment,
        'Change Group': HostsChangeGroup,
        'Assign Compliance Policy': HostsAssignCompliancePolicy,
        'Unassign Compliance Policy': HostsUnassignCompliancePolicy,
        'Change OpenSCAP Capsule': HostsChangeOpenscapCapsule,
        'Assign Location': HostsAssignLocation,
        'Assign Organization': HostsAssignOrganization,
        'Delete Hosts': HostsDeleteActionDialog,
        'Schedule Remote Job': HostsJobInvocationCreateView,
        'Run all Ansible roles': HostsJobInvocationStatusView,
    }

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        action_name = kwargs.get('action_name')
        self.VIEW = self.ACTIONS_VIEWS.get(action_name)
        if not self.VIEW:
            raise ValueError(
                f'Please provide a valid action name. action_name: "{action_name}" not found.'
            )
        entities_list = kwargs.get('entities_list')
        if entities_list == "All":
            self.parent.select_all.fill(True)
        else:
            for entity in entities_list:
                self.parent.table.row(name=entity)[0].widget.fill(True)
        self.parent.actions.fill(action_name)


@navigator.register(HostEntity, 'Recommendations')
class ShowRecommendations(NavigateStep):
    """Navigate to Insights recommendations page"""

    VIEW = CloudInsightsView


@navigator.register(HostEntity, 'InsightsTab')
class InsightsTab(NavigateStep):
    """Navigate to Insights tab on host details page"""

    VIEW = RecommendationListView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Recommendations'].click()


@navigator.register(HostEntity, 'ManageColumns')
class HostsManageColumns(NavigateStep):
    """Navigate to the Manage columns dialog"""

    VIEW = ManageColumnsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        """Open the Manage columns dialog"""
        self.parent.manage_columns.click()


@navigator.register(HostEntity, 'Host Statuses')
class HostStatuses(NavigateStep):
    VIEW = HostStatusesView

    def step(self, *args, **kwargs):
        """Navigate to Monitor -> Host Statuses"""
        self.view.menu.select('Monitor', 'Host Statuses')
