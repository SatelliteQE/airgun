from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.cloud_insights import CloudInsightsView


class CloudInsightsEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_cloud'

    def save_token_sync_hits(self, value):
        """Update Insights cloud view."""
        view = self.navigate_to(self, 'All')
        view.rhcloud_token.fill(value)
        view.save_token.click()


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Insights page"""

    VIEW = CloudInsightsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Insights')
