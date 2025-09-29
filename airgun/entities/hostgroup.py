from navmazing import NavigateToSibling
from wait_for import wait_for
from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.hostgroup import (
    HostGroupCreateView,
    HostGroupEditView,
    HostGroupsView,
)


class HostGroupEntity(BaseEntity):
    endpoint_path = '/hostgroups'

    def create(self, values):
        """Create new host group entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def clone(self, entity_name, values):
        """Clone an existing host group entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Clone')
        view = HostGroupCreateView(self.browser)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for existing host group entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read values from host group edit page"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        value = view.read(widget_names=widget_names)
        view.submit.click()
        return value

    def read_all(self):
        """Read values from host groups title page"""
        view = self.navigate_to(self, 'All')
        return view.read()

    def delete(self, entity_name):
        """Delete host group from the system"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update(self, entity_name, values):
        """Edit an existing host group"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def total_no_of_assigned_role(self, entity_name):
        """Count of assigned role to the host group"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.ansible_roles.click()
        role_list = self.browser.elements(view.ansible_roles.assigned_ansible_role, parent=self)
        wait_for(lambda: int(role_list[-1].text.split('. ')[0]), timeout=30)
        return int(role_list[-1].text.split('. ')[0])

    def assign_role_to_hostgroup(self, entity_name, values):
        """Assign Ansible role(s) to the host group based on user input
        Args:
            entity_name: Name of the host
            values: Name of the ansible role
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def remove_hostgroup_role(self, entity_name, values):
        """Remove Ansible role from the host group based on user input
        Args:
            entity_name: Name of the host
            values: Name of the ansible role
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.ansible_roles.resources.unassigned_values(values)
        view.submit.click()

    def read_role(self, entity_name, values):
        """Return name of the assigned Ansible role(s) of the host group."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.ansible_roles.resources.read_assigned_values(values)


@navigator.register(HostGroupEntity, 'All')
class ShowAllHostGroups(NavigateStep):
    """Navigate to All Host Groups page"""

    VIEW = HostGroupsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Host Groups')


@navigator.register(HostGroupEntity, 'New')
class AddNewHostGroup(NavigateStep):
    """Navigate to Create Host Group page"""

    VIEW = HostGroupCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        try:
            self.parent.new.click()
        except NoSuchElementException:
            self.parent.new_on_blank_page.click()
        self.view.wait_displayed()


@navigator.register(HostGroupEntity, 'Edit')
class EditHostGroup(NavigateStep):
    """Navigate to Edit Host Group page by clicking entity name in the table

    Args:
        entity_name: name of the host group
    """

    VIEW = HostGroupEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
