from time import sleep

from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.exceptions import DisabledWidgetError
from airgun.helpers.host import HostHelper
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.host import HostCreateView
from airgun.views.host import HostDetailsView
from airgun.views.host import HostEditView
from airgun.views.host import HostsAssignCompliancePolicy
from airgun.views.host import HostsAssignLocation
from airgun.views.host import HostsAssignOrganization
from airgun.views.host import HostsChangeEnvironment
from airgun.views.host import HostsChangeGroup
from airgun.views.host import HostsDeleteActionDialog
from airgun.views.host import HostsDeleteTaskDetailsView
from airgun.views.host import HostsJobInvocationCreateView
from airgun.views.host import HostsJobInvocationStatusView
from airgun.views.host import HostsView


class HostEntity(BaseEntity):
    endpoint_path = '/hosts'

    HELPER_CLASS = HostHelper

    def create(self, values):
        """Create new host entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        self.browser.click(view.submit, ignore_ajax=True)
        self.browser.plugin.ensure_page_safe(timeout='600s')
        host_view = HostDetailsView(self.browser)
        wait_for(
            lambda: host_view.is_displayed is True,
            timeout=60,
            delay=1,
            logger=host_view.logger
        )
        host_view.flash.assert_no_error()
        host_view.flash.dismiss()

    def search(self, value):
        """Search for existing host entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

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
        alert_message = self.browser.get_alert().text
        self.browser.handle_alert(cancel=cancel)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return alert_message

    def delete_interface(self, entity_name, interface_id):
        """Delete host network interface.

        :param entity_name: The host name to delete the network interface from
        :param interface_id: The network interface identifier.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        delete_button = view.interfaces.interfaces_list.row(
            identifier=interface_id)['Actions'].widget.delete
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

    def _select_action(self, action_name, entities_list):
        """Navigate to all entities, select the entities, and returns the view
        of the selected action name from main entity select action dropdown.
        """
        return self.navigate_to(
            self,
            'Select Action',
            action_name=action_name,
            entities_list=entities_list
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

    def export(self):
        """Export hosts list.

         :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        view.export.click()
        return self.browser.save_downloaded_file()

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
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        status_view = HostsJobInvocationStatusView(self.browser)
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
        return view.parameters.puppet_class_parameters.row(name=name)['Value'].widget.read()

    def set_puppet_class_parameter_value(self, entity_name, name, value):
        """Set Puppet class parameter value

        :param str entity_name: The host name for which to set the parameter value.
        :param str name: the parameter name.
        :param dict value: The parameter value
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)  # type: HostEditView
        view.parameters.puppet_class_parameters.row(name=name).fill({'Value': value})
        view.submit.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_webconsole_content(self, entity_name):
        """Navigate to host's webconsole and return the hostname from the cockpit page

        :param str entity_name: The host name for which to set the parameter value.
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.webconsole.click()
        view.validations.assert_no_errors()
        # the remote host content is loaded in an iframe, let's switch to it
        self.browser.selenium.switch_to.frame(0)
        hostname_button_view = self.browser.selenium.find_elements_by_id(
            'system_information_hostname_button'
        )
        wait_for(
            lambda: hostname_button_view[0].text != '',
            handle_exception=True, timeout=10,
            logger=view.logger
        )
        hostname = hostname_button_view[0].text
        self.browser.switch_to_main_frame()
        return hostname


@navigator.register(HostEntity, 'All')
class ShowAllHosts(NavigateStep):
    """Navigate to All Hosts page"""
    VIEW = HostsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')


@navigator.register(HostEntity, 'New')
class AddNewHost(NavigateStep):
    """Navigate to Create Host page"""
    VIEW = HostCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


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


@navigator.register(HostEntity, 'Select Action')
class HostsSelectAction(NavigateStep):
    """Navigate to Action page by selecting checkboxes for necessary hosts and
     then clicking on the action name button in 'Select Action' dropdown.

    Args:
        action_name: the action name to select from dropdown button
        entities_list: list of hosts that need to be modified
    """
    ACTIONS_VIEWS = {
        'Change Environment': HostsChangeEnvironment,
        'Change Group': HostsChangeGroup,
        'Assign Compliance Policy': HostsAssignCompliancePolicy,
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
            raise ValueError('Please provide a valid action name.'
                             ' action_name: "{0}" not found.')
        entities_list = kwargs.get('entities_list')
        if entities_list == "All":
            self.parent.select_all.fill(True)
        else:
            for entity in entities_list:
                self.parent.table.row(name=entity)[0].widget.fill(True)
        self.parent.actions.fill(action_name)
