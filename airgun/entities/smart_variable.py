from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.smart_variable import (
    SmartVariableCreateView,
    SmartVariableEditView,
    SmartVariablesTableView,
)


class SmartVariableEntity(BaseEntity):

    def create(self, values):
        """Create new smart variable entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for smart variable entity and return table row that contains
        that entity
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read all values for existing smart variable entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update specific smart variable values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete smart variable entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(username=entity_name)['Actions'].widget.click(
            handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(SmartVariableEntity, 'All')
class ShowAllSmartVariables(NavigateStep):
    """Navigate to All Smart Variables screen."""
    VIEW = SmartVariablesTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Smart Variables')


@navigator.register(SmartVariableEntity, 'New')
class AddNewSmartVariable(NavigateStep):
    """Navigate to Create Smart Variable screen."""
    VIEW = SmartVariableCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(SmartVariableEntity, 'Edit')
class EditSmartVariable(NavigateStep):
    """Navigate to Edit Smart Variable screen.

        Args:
            entity_name: name of smart variable
    """
    VIEW = SmartVariableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(variable=entity_name)['Variable'].widget.click()
