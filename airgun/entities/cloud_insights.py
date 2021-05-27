from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.cloud_insights import CloudInsightsView


class CloudInsightsEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_cloud'

    def search(self, value):
        """Search for 'value' and return hostname/recommendation names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def remediate(self, entity_name):
        """Delete existing content host"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.select_all.fill(True)
        view.select_all_hits.click()
        # view.remediate.click()
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read_all(self, widget_names=None):
        """Return dict with properties of RH Cloud - Insights."""
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

    def save_token_sync_hits(self, value):
        """Update Insights cloud view."""
        view = self.navigate_to(self, 'All')
        view.rhcloud_token.fill(value)
        view.save_token.click()

    def update(self, values):
        """Update RH Cloud - Insights view."""
        view = self.navigate_to(self, 'All')
        view.fill(values)


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Insights page"""

    VIEW = CloudInsightsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Insights')
