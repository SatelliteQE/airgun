from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.common import BaseLoggedInView
from airgun.views.settings import SettingsView


class SettingsEntity(BaseEntity):
    endpoint_path = '/settings'

    def search(self, value):
        """Search for necessary settings entry"""
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

    def send_test_mail(self, property_name):
        """Send the mail to the recipient"""
        view = self.navigate_to(self, 'All')
        view.search(property_name)
        view.Email.test_email_button.click()
        return view.flash.read()

    def permission_denied(self):
        """Return permission denied error text"""
        view = BaseLoggedInView(self.browser)
        return view.permission_denied.text


@navigator.register(SettingsEntity, 'All')
class ShowAllSettings(NavigateStep):
    """Navigate to All Settings page"""

    VIEW = SettingsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Settings')
