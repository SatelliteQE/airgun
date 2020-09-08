from time import sleep

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.oscapreports import DeletereportsDialog
from airgun.views.oscapreports import OSCAPReportsView


class OSCAPReportsEntity(BaseEntity):
    endpoint_path = '/compliance/arf_reports'

    def search(self, value):
        """Search for existing Compliance Reports."""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_all(self):
        """Read all values from Compliance Reports page."""
        view = self.navigate_to(self, 'All')
        return view.read()

    def delete(self, search_pattern, cancel=False):
        """Delete first Compliance Report based on search_pattern."""
        view = self.navigate_to(self, 'All')
        view.search(search_pattern)
        view.table.row()['Actions'].widget.fill('Delete')
        alert_message = self.browser.get_alert().text
        self.browser.handle_alert(cancel=cancel)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return alert_message

    def full_report(self, search_pattern, cancel=False):
        """View Full Compliance Report."""
        view = self.navigate_to(self, 'All')
        view.search(search_pattern)
        view.table.row()['Actions'].widget.fill('Full Report')

    def delete_reports(self, search_pattern):
        """Delete all reports based on search_pattern
           If keyword 'All' is supplied, all reports are selected
           using the checkbox from table header
        """
        view = self.navigate_to(self, 'Delete reports', search_pattern=search_pattern)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(OSCAPReportsEntity, 'All')
class ShowAllHosts(NavigateStep):
    """Navigate to Compliance Reports page."""
    VIEW = OSCAPReportsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Reports')


@navigator.register(OSCAPReportsEntity, 'Delete reports')
class ReportsSelectAction(NavigateStep):
    """Navigate to Delete reports page by selecting checkboxes for necessary reports.

    Args:
        search_pattern: search_pattern to select reports.
    """
    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        search_pattern = kwargs.get('search_pattern')
        self.VIEW = DeletereportsDialog
        if search_pattern != "All":
            self.parent.search(search_pattern)
        self.parent.select_all.fill(True)
        self.parent.delete_reports.click()
