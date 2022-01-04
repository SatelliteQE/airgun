from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.configgroup import ConfigGroupCreateView
from airgun.views.configgroup import ConfigGroupEditView
from airgun.views.configgroup import ConfigGroupsView


class ConfigGroupEntity(BaseEntity):
    endpoint_path = '/config_groups'

    def create(self, values):
        """Create new config group"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for existing config group"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read existing config group"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update config group"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete config group"""
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ConfigGroupEntity, 'All')
class ShowAllConfigGroups(NavigateStep):
    """Navigate to All Config Groups screen."""

    VIEW = ConfigGroupsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Config Groups')


@navigator.register(ConfigGroupEntity, 'New')
class AddNewConfigGroup(NavigateStep):
    """Navigate to Create new Config Group screen."""

    VIEW = ConfigGroupCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ConfigGroupEntity, 'Edit')
class EditConfigGroup(NavigateStep):
    """Navigate to Edit Config Group screen.

    Args:
        entity_name: name of config group
    """

    VIEW = ConfigGroupEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
