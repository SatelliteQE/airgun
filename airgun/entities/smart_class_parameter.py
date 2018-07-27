from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.smart_class_parameter import (
    SmartClassParameterEditView,
    SmartClassParametersView,
)


class SmartClassParameterEntity(BaseEntity):

    def search(self, value):
        """Search for smart class parameter entity and return table row that
        contains that entity
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read all values for existing smart class parameter entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update specific smart class parameter values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(SmartClassParameterEntity, 'All')
class ShowAllSmartClassParameters(NavigateStep):
    """Navigate to All Smart Class Parameter screen."""
    VIEW = SmartClassParametersView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Smart Class Parameters')


@navigator.register(SmartClassParameterEntity, 'Edit')
class EditSmartClassParameter(NavigateStep):
    """Navigate to Edit Smart Class Parameter screen.

        Args:
            entity_name: name of smart class parameter
    """
    VIEW = SmartClassParameterEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(
            parameter=entity_name)['Parameter'].widget.click()
