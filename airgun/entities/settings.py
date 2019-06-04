from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.settings import SettingEditView, SettingsView


class SettingsEntity(BaseEntity):
    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, property_name, widget_names=None):
        """Read settings values"""
        view = self.navigate_to(self, 'All')
        view.search(property_name)
        result = view.read(widget_names=widget_names)
        view.menu.select('Administer', 'About')
        return result

    def update(self, property_name, value):
        """Update setting property with provided value"""
        view = self.navigate_to(self, 'Edit', property_name=property_name)
        view.table.row()['Value'].widget.fill(value)
        view.table.row()['Value'].widget.submit.click()
        view.validations.assert_no_errors()
        view.wait_for_update()
        view.menu.select('Administer', 'About')


@navigator.register(SettingsEntity, 'Edit')
class EditSetting(NavigateStep):
    """Navigate to Edit Settings view

    Args:
        property_name: name of Property in Settings
    """
    VIEW = SettingEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        property_name = kwargs.get('property_name')
        self.parent.search(property_name)
        self.parent.table.row()['Value'].widget.click()


@navigator.register(SettingsEntity, 'All')
class ShowAllSettings(NavigateStep):
    """Navigate to All Settings page"""
    VIEW = SettingsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Settings')
