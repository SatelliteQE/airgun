from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_insights import (
    CloudInsightsView,
    CloudTokenView,
    RecommendationsDetails,
    RecommendationsTabView,
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
        view.remediation_window.remediate.click()

    def sync_hits(self):
        """Sync Insights recommendations."""
        view = self.navigate_to(self, 'All')
        view.insights_dropdown.wait_displayed()
        view.insights_dropdown.item_select('Sync recommendations')
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

class RecommendationsTabEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_cloud'

    def search(self, value):
        """Search for 'query' and return matched hostnames/recommendations.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        view.clear_button.click()
        view.search_field.fill(value)
        return self.table.read()

    def affected_systems(self, recommendation_name: str, hostname: str):
        """Open Affected systems, filter by hostname, select it, and click Remediate.

        Returns the details view contents after remediation click.
        """
        view = self.navigate_to(self, 'All')
        view.clear_button.click()
        view.search_field.fill(recommendation_name)
        # Allow the table to refresh after searching
        self.browser.plugin.ensure_page_safe(timeout='30s')
        view.table.wait_displayed()
        # recommendation_view = RecommendationsTabView(self.browser)
        # recommendation_view.wait_displayed()
        # # Wait for the affected systems table to be present and visible
        # self.browser.wait_for_element(recommendation_view.table, ensure_page_safe=True, exception=False)
        row = view.table.row(name=recommendation_name)
        row.expand()
        row.content.affected_systems_url.click()
        # Ensure navigation completed and affected systems view is fully loaded
        #self.browser.plugin.ensure_page_safe(timeout='30s')
        details_view = RecommendationsDetails(self.browser)
        details_view.wait_displayed()
        # Wait for the affected systems table to be present and visible
        self.browser.wait_for_element(details_view.table, ensure_page_safe=True, exception=False)
        details_view.table.wait_displayed()
        # Filter by hostname and wait for results
        details_view.search_field.fill(hostname)
        self.browser.plugin.ensure_page_safe(timeout='15s')
        details_view.table.wait_displayed()

        # Select the target host row and remediate
        host_row = details_view.table.row(name=hostname)
        host_row[0].widget.fill(True)
        details_view.remediate.click()
        self.browser.plugin.ensure_page_safe(timeout='30s')

        return details_view.read()

    def read(self, widget_names=None):
        """Read all values."""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='10s')
        view.wait_displayed()
        return view.read(widget_names=widget_names)

@navigator.register(CloudInsightsEntity, 'Token')
class SaveCloudTokenView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = CloudTokenView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed')


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = CloudInsightsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Recommendations')


@navigator.register(RecommendationsTabEntity, 'All')
class ShowRecommendationsView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = RecommendationsTabView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Recommendations')
