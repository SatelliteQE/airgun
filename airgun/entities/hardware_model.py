from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.hardware_model import HardwareModelCreateView
from airgun.views.hardware_model import HardwareModelEditView
from airgun.views.hardware_model import HardwareModelsView


class HardwareModelEntity(BaseEntity):
    endpoint_path = '/models'

    def create(self, values):
        """Create new hardware model"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific hardware model"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read values for existing hardware model"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update hardware model values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name, err_message=''):
        """Delete hardware model

        err_message - expected when dialog throws an error, error message is checked
        """
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click()
        view.delete_dialog.confirm()
        if err_message:
            view.flash.assert_message(err_message)
            view.flash.dismiss()
            view.delete_dialog.cancel()
        else:
            view.flash.assert_no_error()
            view.flash.dismiss()


@navigator.register(HardwareModelEntity, 'All')
class ShowAllHardwareModels(NavigateStep):
    """Navigate to All Hardware Model screen."""

    VIEW = HardwareModelsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Hardware Models')


@navigator.register(HardwareModelEntity, 'New')
class AddNewHardwareModel(NavigateStep):
    """Navigate to Create new Hardware Model screen."""

    VIEW = HardwareModelCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HardwareModelEntity, 'Edit')
class EditHardwareModel(NavigateStep):
    """Navigate to Edit Hardware Model screen.

    Args:
       entity_name: name of hardware model
    """

    VIEW = HardwareModelEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
