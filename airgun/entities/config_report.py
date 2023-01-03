from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.config_report import ConfigReportDetailsView
from airgun.views.config_report import ConfigReportsView


class ConfigReportEntity(BaseEntity):
    endpoint_path = '/config_reports'

    def read(self, widget_names=None, host_name=None):
        """Read all values for generated Config Reports"""
        view = self.navigate_to(self, 'All')
        if host_name:
            view.search(host_name)
        return view.read(widget_names=widget_names)

    def search(self, hostname):
        """Search for specific Config report"""
        view = self.navigate_to(self, 'Report Details', host_name=hostname)
        return view.read()

    def export(self, host_name=None):
        """Export a Config report.

        :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        if host_name:
            view.search(host_name)
        view.export.click()
        return self.browser.save_downloaded_file()

    def delete(self, host_name):
        """Delete a Config report"""
        view = self.navigate_to(self, 'All')
        view.search(host_name)
        view.table.row()['Actions'].widget.click()
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ConfigReportEntity, 'All')
class ShowAllConfigReports(NavigateStep):
    """Navigate to all Config Report screen."""

    VIEW = ConfigReportsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Config Management')


@navigator.register(ConfigReportEntity, 'Report Details')
class ConfigReportStatus(NavigateStep):
    """Navigate to Config Report details screen.

    Args:host_name: name of the host to which job was applied
    """

    VIEW = ConfigReportDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(f'host = {kwargs.get("host_name")}')
        self.parent.table.row()['Last report'].widget.click()
