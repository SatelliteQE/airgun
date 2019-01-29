from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.hostgroup import (
    HostGroupCreateView,
    HostGroupEditView,
    HostGroupsView,
)


class HostGroupEntity(BaseEntity):

    def create(self, values):
        """Create new host group entity"""
        view = self.navigate_to(self, 'New')
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
        return view.read(widget_names=widget_names)

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


@navigator.register(HostGroupEntity, 'All')
class ShowAllHostGroups(NavigateStep):
    """Navigate to All Host Groups page"""
    VIEW = HostGroupsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Host Group')


@navigator.register(HostGroupEntity, 'New')
class AddNewHostGroup(NavigateStep):
    """Navigate to Create Host Group page"""
    VIEW = HostGroupCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


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
