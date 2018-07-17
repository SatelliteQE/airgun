from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.host import (
    HostCreateView,
    HostDetailsView,
    HostEditView,
    HostsChangeGroup,
    HostsChangeEnvironment,
    HostsView,
)


class HostEntity(BaseEntity):

    def create(self, values):
        """Create new host entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for existing host entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def get_details(self, entity_name):
        """Read host values from Host Details page"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read()

    def read(self, entity_name):
        """Read host values from Host Edit page"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def delete(self, entity_name):
        """Delete host from the system"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def change_host_group(self, entities_list, values):
        """Change assigned host group for host/hosts"""
        view = self.navigate_to(
            self, 'Change Group', entities_list=entities_list)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def change_host_environment(self, entities_list, values):
        """Change assigned environment for host/hosts"""
        view = self.navigate_to(
            self, 'Change Environment', entities_list=entities_list)
        view.fill(values)
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


@navigator.register(HostEntity, 'Change Group')
class AssignHostGroup(NavigateStep):
    """Navigate to Change Host Group page by selecting checkboxes for necessary
    hosts and then clicking on 'Change Group' button in 'Select Action'
    dropdown

    Args:
        entities_list: list of hosts that need to be modified
    """
    VIEW = HostsChangeGroup

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entities_list = kwargs.get('entities_list')
        for entity in entities_list:
            self.parent.table.row(name=entity)[0].widget.fill(True)
        self.parent.actions.fill('Change Group')


@navigator.register(HostEntity, 'Change Environment')
class AssignHostEnvironment(NavigateStep):
    """Navigate to Change Puppet Environment page by selecting checkboxes for
    necessary hosts and then clicking on 'Change Environment' button in 'Select
    Action' dropdown

    Args:
        entities_list: list of hosts that need to be modified
    """
    VIEW = HostsChangeEnvironment

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entities_list = kwargs.get('entities_list')
        for entity in entities_list:
            self.parent.table.row(name=entity)[0].widget.fill(True)
        self.parent.actions.fill('Change Environment')
