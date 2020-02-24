from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.discoveredhosts import DiscoveredHostDetailsView
from airgun.views.discoveredhosts import DiscoveredHostEditProvisioningView
from airgun.views.discoveredhosts import DiscoveredHostProvisionDialog
from airgun.views.discoveredhosts import DiscoveredHostsAssignLocationDialog
from airgun.views.discoveredhosts import DiscoveredHostsAssignOrganizationDialog
from airgun.views.discoveredhosts import DiscoveredHostsAutoProvisionDialog
from airgun.views.discoveredhosts import DiscoveredHostsDeleteDialog
from airgun.views.discoveredhosts import DiscoveredHostsRebootDialog
from airgun.views.discoveredhosts import DiscoveredHostsView


class DiscoveredHostsEntity(BaseEntity):
    endpoint_path = '/discovered_hosts'

    def wait_for_entity(self, entity_name):
        """Wait for a host to be discovered providing the expected entity_name

        Note: When no discovered host exists is in the system, the search box
            does not exist in the DOM, and as we are waiting for a host to be
            discovered we have to ensure that the view became searchable.

        :raise TimedOutError if the view will not became searchable in time
        :raise TimedOutError if the host is not discovered in time
        :returns the entity table row columns values
        """
        view = self.navigate_to(self, 'All')
        wait_for(
            lambda: view.is_searchable(),
            fail_condition=False,
            timeout=300,
            delay=10,
            fail_func=view.browser.refresh,
            logger=view.logger
        )
        result = wait_for(
            lambda: view.search('name = "{0}"'.format(entity_name)),
            fail_condition=[],
            timeout=300,
            delay=10,
            logger=view.logger
        )
        return result.out[0]

    def search(self, value):
        """Search for 'value' and return discovery hosts values that match.

        :param str value: filter text.
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def delete(self, entity_name):
        """Delete discovered host with name entity_name"""
        return self.apply_action('Delete', entity_name)

    def read(self, entity_name, widget_names=None):
        """Return a dict with properties of discovered host."""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def provision(self, entity_name, host_group, organization, location,
                  quick=True, host_values=None):
        """Provision a discovered host with name entity_name.

        :param str entity_name: The discovered host name.
        :param str host_group: The hostgroup to select for the host
            provisioning.
        :param str organization: The Organization to select for the host
            provisioning.
        :param str location: the Location to select for host provisioning.
        :param bool quick: Whether to proceed to provisioning with default
            values. If not a custom host edit dialog will appear to edit the
            custom values.
        :param dict host_values: The custom host provisioning values to fill
            the custom host view that appear in case of not quick procedure.
        """
        if host_values is None:
            host_values = {}

        view = self.navigate_to(self, 'Provision', entity_name=entity_name)
        view.fill(dict(
            host_group=host_group,
            organization=organization,
            location=location,
        ))
        if quick:
            view.quick_create.click()
        else:
            view.customize_create.click()
            discovered_host_edit_view = DiscoveredHostEditProvisioningView(
                self.browser)
            discovered_host_edit_view.fill(host_values)
            self.browser.click(
                discovered_host_edit_view.submit, ignore_ajax=True)
            self.browser.plugin.ensure_page_safe(timeout='120s')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def apply_action(self, action_name, entities_list, values=None):
        """Apply action name for discovered hosts.

        :param str action_name: The action name to apply, available:
            'Assign Location', 'Assign Organization', 'Auto Provision',
            'Delete', 'Reboot'
        :param List[str] entities_list: Discovered hosts name list.
        :param dict values: The values to fill the action form dialog with.
        """
        if values is None:
            values = {}
        view = self.navigate_to(self, 'Select Action', action_name=action_name,
                                entities_list=entities_list)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(DiscoveredHostsEntity, 'All')
class ShowAllDiscoveredHosts(NavigateStep):
    """Navigate to All Discovered hosts screen."""
    VIEW = DiscoveredHostsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Discovered Hosts')


@navigator.register(DiscoveredHostsEntity, 'Details')
class ShowDiscoveredHostDetailsView(NavigateStep):
    """Navigate to Discovered Host details screen."""
    VIEW = DiscoveredHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search('name = {0}'.format(entity_name))
        self.parent.table.row_by_cell_or_widget_value(
            'Name', entity_name)['Name'].widget.click()


@navigator.register(DiscoveredHostsEntity, 'Select Action')
class DiscoveredHostsSelectAction(NavigateStep):
    """Navigate to Action page by selecting checkboxes for necessary discovered
    hosts and then clicking on the action name button in 'Select Action'
    dropdown.

    Args:
        action_name: the action name to select from dropdown button
        entities_list: list of discovered hosts that need to apply action on.
    """
    ACTIONS_VIEWS = {
        'Assign Location': DiscoveredHostsAssignLocationDialog,
        'Assign Organization': DiscoveredHostsAssignOrganizationDialog,
        'Auto Provision': DiscoveredHostsAutoProvisionDialog,
        'Delete': DiscoveredHostsDeleteDialog,
        'Reboot': DiscoveredHostsRebootDialog
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
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        for entity_name in entities_list:
            self.parent.table.row_by_cell_or_widget_value(
                'Name', entity_name)[0].widget.click()
        self.parent.actions.fill(action_name)


@navigator.register(DiscoveredHostsEntity, 'Provision')
class DiscoveredHostProvisionActionNavigation(NavigateStep):

    VIEW = DiscoveredHostProvisionDialog

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.navigate_to(self.obj, 'Details', entity_name=entity_name)

    def step(self, *args, **kwargs):
        self.parent.actions.fill('Provision')
