from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.discoveredhosts import (
    DiscoveredHostEditProvisioningView,
    DiscoveredHostDetailsView,
    DiscoveredHostProvisionDialog,
    DiscoveredHostsAssignLocationDialog,
    DiscoveredHostsAssignOrganizationDialog,
    DiscoveredHostsAutoProvisionDialog,
    DiscoveredHostsDeleteDialog,
    DiscoveredHostsRebootDialog,
    DiscoveredHostsView,
)


class DiscoveredHostsEntity(BaseEntity):

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

    def read(self, entity_name):
        """Return a dict with properties of discovered host."""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read()

    def provision(self, entity_name, host_group, organization, location,
                  quick=True, host_values=None):
        """Provision a discovered host with name entity_name."""
        if host_values is None:
            host_values = {}

        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.actions.fill('Provision')
        dialog_view = DiscoveredHostProvisionDialog(self.browser)
        dialog_view.fill(dict(
            host_group=host_group,
            organization=organization,
            location=location,
        ))
        if quick:
            dialog_view.quick_create.click()
        else:
            dialog_view.customize_create.click()
            discovered_host_edit_view = DiscoveredHostEditProvisioningView(
                self.browser)
            discovered_host_edit_view.fill(host_values)
            discovered_host_edit_view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def auto_provision(self, entities_list):
        """Auto provision discovered hosts which names supplied in
        entities_list.
        """
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        view = self.navigate_to(
            self, 'Auto Provision', entities_list=entities_list)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def reboot(self, entities_list):
        """Reboot discovered hosts which names supplied in entities_list."""
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        view = self.navigate_to(
            self, 'Reboot', entities_list=entities_list)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def assign_organization(self, entities_list, organization):
        """Assign a new organization to discovered hosts which names supplied
        in entities_list."""
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        view = self.navigate_to(
            self, 'Assign Organization', entities_list=entities_list)
        view.organization.fill(organization)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def assign_location(self, entities_list, location):
        """Assign a new location to discovered hosts which names supplied
        in entities_list."""
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        view = self.navigate_to(
            self, 'Assign Location', entities_list=entities_list)
        view.location.fill(location)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entities_list):
        """Delete discovered hosts which names supplied in entities_list."""
        if not isinstance(entities_list, (list, tuple)):
            entities_list = [entities_list]
        view = self.navigate_to(
            self, 'Delete', entities_list=entities_list)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(DiscoveredHostsEntity, 'All')
class ShowAllDiscoveredHosts(NavigateStep):
    """Navigate to All Discovered hosts screen."""
    VIEW = DiscoveredHostsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Discovered hosts')


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


class DiscoveredHostsActionNavigation(NavigateStep):
    """Common NavigateStep to discovered hosts entity actions,
    Navigate to ACTION_NAME dialog by selecting checkboxes for necessary
    discovered hosts and then clicking on 'ACTION_NAME' button in
    'Select Action' dropdown.

    Args:
        entities_list: list of discovered hosts to select and apply the action.
    """
    VIEW = None
    ACTION_NAME = None

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entities_list = kwargs.get('entities_list')
        for entity_name in entities_list:
            self.parent.table.row_by_cell_or_widget_value(
                'Name', entity_name)[0].widget.click()
        self.parent.actions.fill(self.ACTION_NAME)


@navigator.register(DiscoveredHostsEntity, 'Auto Provision')
class AutoProvisionDiscoveredHosts(DiscoveredHostsActionNavigation):
    """Navigate to discovered hosts Auto Provision dialog view"""
    VIEW = DiscoveredHostsAutoProvisionDialog
    ACTION_NAME = 'Auto Provision'


@navigator.register(DiscoveredHostsEntity, 'Delete')
class DeleteDiscoveredHosts(DiscoveredHostsActionNavigation):
    """Navigate to discovered hosts Delete dialog view"""
    VIEW = DiscoveredHostsDeleteDialog
    ACTION_NAME = 'Delete'


@navigator.register(DiscoveredHostsEntity, 'Assign Organization')
class AssignOrganizationDiscoveredHosts(DiscoveredHostsActionNavigation):
    """Navigate to discovered hosts Assign Organization dialog view"""
    VIEW = DiscoveredHostsAssignOrganizationDialog
    ACTION_NAME = 'Assign Organization'


@navigator.register(DiscoveredHostsEntity, 'Assign Location')
class AssignLocationDiscoveredHosts(DiscoveredHostsActionNavigation):
    """Navigate to discovered hosts Assign Location dialog view"""
    VIEW = DiscoveredHostsAssignLocationDialog
    ACTION_NAME = 'Assign Location'


@navigator.register(DiscoveredHostsEntity, 'Reboot')
class RebootDiscoveredHosts(DiscoveredHostsActionNavigation):
    """Navigate to discovered hosts Reboot dialog view"""
    VIEW = DiscoveredHostsRebootDialog
    ACTION_NAME = 'Reboot'
