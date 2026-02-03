from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.cloud_insights import (
    CloudInsightsView,
    RecommendationsDetailsView,
    RecommendationsTabView,
    RemediateSummary,
)
from airgun.views.job_invocation import JobInvocationStatusView


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
        view.insights_dropdown.item_select('Sync recommendations')

    def read(self, widget_names=None):
        """Read all values."""
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

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
        view = self.navigate_to(self, 'All Recommendations')
        view.reset_filters()
        view.search(value)
        return view.table.read()

    def remediate_affected_system(self, recommendation_name, hostname):
        """Open Affected systems, filter by hostname, select it, and click Remediate.

        Returns the details view contents after remediation click.
        """
        # Navigate to the Recommendation's Affected Systems
        view = self.navigate_to(self, 'Affected Systems', recommendation_name=recommendation_name)

        # Filter by hostname
        view.search(hostname)
        # FIXME: remove wait_for
        wait_for(lambda: view.table.row(name=hostname), handle_exception=True, timeout=20)

        # Select host and click 'Remediate'
        view.table[0][0].widget.click()
        view.remediate.click()

        # Wait for Remediation modal to display, then submit it
        modal = RemediateSummary(self.browser)
        modal.wait_displayed()
        modal.remediate.click()

        # Wait for the remote execution job to complete
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()

        return view.read()

    def bulk_remediate_affected_systems(self, recommendation_name):
        """Open Affected systems, bulk select affected systems, and click Remediate.

        Returns the details view contents after remediation click.
        """
        # Navigate to the Recommendation's Affected Systems
        view = self.navigate_to(self, 'Affected Systems', recommendation_name=recommendation_name)

        # TODO: remove wait_for
        wait_for(lambda: view.table.row(), handle_exception=True, timeout=20)

        # Select all hosts and click 'Remediate'
        view.bulk_select.select_all()
        view.remediate.click()

        # Wait for Remediation modal to display, then submit it
        modal = RemediateSummary(self.browser)
        modal.wait_displayed()
        modal.remediate.click()

        # Wait for the remote execution job to complete
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()

        return view.read()

    def apply_filter(self, filter_type, filter_value):
        """
        Apply a filter to the recommendations table.

        Returns:
            Table data after filtering is applied.

        Example:
            session.recommendationstab.apply_filter("Status", "Disabled")
        """
        view = self.navigate_to(self, 'All Recommendations')
        # TODO: verify this
        view.menu_toggle.fill(filter_type)
        view.menu_filter.fill(filter_value)
        return view.table.read()

    def read(self, widget_names=None):
        """Read all values."""
        view = self.navigate_to(self, 'All Recommendations')
        return view.read(widget_names=widget_names)


@navigator.register(RecommendationsTabEntity, 'Affected Systems')
class NavigateToAffectedSystems(NavigateStep):
    """Navigate from Recommendations tab to the Affected Systems details view."""

    VIEW = RecommendationsDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All Recommendations')

    def step(self, *args, **kwargs):
        recommendation_name = kwargs.get('recommendation_name')
        # Filter by recommendation name and open its expanded content

        self.parent.reset_filters()
        self.parent.search(recommendation_name)

        # TODO: remove wait_for
        row, _ = wait_for(lambda: self.parent.table.row(name=recommendation_name), timeout=5)

        row.expand()
        row.content.affected_systems_url.click()


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = CloudInsightsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Recommendations')


@navigator.register(RecommendationsTabEntity, 'All Recommendations')
class ShowRecommendationsView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = RecommendationsTabView

    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Recommendations')
