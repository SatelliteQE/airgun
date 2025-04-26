import time

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_insights import (
    CloudInsightsView,
    CloudTokenView,
    RemediationView,
)


class CloudInsightsEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_cloud'

    def search(self, value):
        """Search for 'query' and return matched hostnames/recommendations.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def remediate(self, entity_name):
        """Remediate hosts based on search input."""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.select_all.fill(True)
        view.select_all_hits.click()
        view.remediate.click()

        view = RemediationView(self.browser)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()

        view.remediate.click()

        # FIXME sleep to allow API call to complete
        time.sleep(2)
        self.browser.plugin.ensure_page_safe()

    def sync_hits(self):
        """Sync Insights recommendations."""
        view = self.navigate_to(self, 'All')
        view.insights_dropdown.wait_displayed()
        view.insights_dropdown.item_select('Sync recommendations')

        # FIXME sleep to allow API call to complete.
        time.sleep(2)
        self.browser.plugin.ensure_page_safe(timeout='60s')

    def read(self, widget_names=None):
        """Read all values."""
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

    def save_token_sync_hits(self, value):
        """Update Insights cloud view."""
        view = self.navigate_to(self, 'Token')
        view.rhcloud_token.fill(value)
        view.save_token.click()
        self.browser.plugin.ensure_page_safe(timeout='60s')

    def update(self, values):
        """Update Insights view."""
        view = self.navigate_to(self, 'All')
        view.fill(values)


@navigator.register(CloudInsightsEntity, 'Token')
class SaveCloudTokenView(NavigateStep):
    """Navigate to main Red Hat Insights page"""

    VIEW = CloudTokenView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Insights')


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Insights page"""

    VIEW = CloudInsightsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Insights', 'Recommendations')
