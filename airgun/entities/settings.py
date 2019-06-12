from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.settings import SettingsView


class SettingsEntity(BaseEntity):
    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, property_name):
        """Read settings values"""
        view = self.navigate_to(self, 'All')
        view.search(property_name)
        return view.read()

    def update(self, property_name, value):
        """Update setting property with provided value"""
        view = self.navigate_to(self, 'All')
        view.search(property_name)
        view.table.row()['Value'].widget.fill(value)
        view.validations.assert_no_errors()
        view.wait_for_update()


@navigator.register(SettingsEntity, 'All')
class ShowAllSettings(NavigateStep):
    """Navigate to All Settings page"""
    VIEW = SettingsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Settings')
