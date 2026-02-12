import time

from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_insights import (
    CloudInsightsView,
    CloudTokenView,
    DisableRecommendationModal,
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
        view = self.navigate_to(self, 'All Recommendations')
        view.wait_displayed(timeout=10)
        wait_for(lambda: view.clear_button.is_displayed, handle_exception=True, timeout=20)
        view.clear_button.click()
        view.search_field.fill(value)
        time.sleep(5)
        return view.table.read()

    def remediate_affected_system(self, recommendation_name, hostname):
        """Open Affected systems, filter by hostname, select it, and click Remediate.

        :return: the details view contents after remediation click.
        """
        # Use navigator to open the Affected Systems details view
        view = self.navigate_to(self, 'Affected Systems', recommendation_name=recommendation_name)
        view.search_field.wait_displayed()
        # Filter by hostname and apply recommendation
        view.search_field.fill(hostname)
        wait_for(lambda: view.table.row(name=hostname), handle_exception=True, timeout=20)
        time.sleep(15)
        view.table[0][0].widget.click()
        view.remediate.click()
        self.browser.plugin.ensure_page_safe(timeout='30s')
        modal = RemediateSummary(self.browser)
        wait_for(lambda: modal.is_displayed, handle_exception=True, timeout=20)
        modal.remediate.click()
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()
        return view.read()

    def bulk_remediate_affected_systems(self, recommendation_name):
        """Open Affected systems, bulk select affected systems, and click Remediate.

        :return: the details view contents after remediation click.
        """
        # Use navigator to open the Affected Systems details view
        view = self.navigate_to(self, 'Affected Systems', recommendation_name=recommendation_name)
        wait_for(lambda: view.table.row(), handle_exception=True, timeout=20)
        time.sleep(5)
        view.bulk_select.select_all()
        view.remediate.click()
        self.browser.plugin.ensure_page_safe(timeout='30s')
        modal = RemediateSummary(self.browser)
        wait_for(lambda: modal.is_displayed, handle_exception=True, timeout=20)
        modal.remediate.click()
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()
        return view.read()

    def apply_filter(self, filter_type, filter_value):
        """
        Apply a filter to the recommendations table.

        :return: Table data after filtering is applied

        :example: session.recommendationstab.apply_filter("Status", "Disabled")
        """
        view = self.navigate_to(self, 'All Recommendations')

        self.browser.plugin.ensure_page_safe(timeout='10s')
        wait_for(lambda: view.table.is_displayed, timeout=20, handle_exception=True)
        view.clear_button.click()
        view.menu_toggle.fill(filter_type)
        view.menu_filter.fill(filter_value)
        self.browser.plugin.ensure_page_safe(timeout='10s')
        wait_for(lambda: view.table.is_displayed, timeout=20, handle_exception=True)
        return view.table.read()

    def read(self, widget_names=None):
        """Read all values."""
        view = self.navigate_to(self, 'All Recommendations')
        self.browser.plugin.ensure_page_safe(timeout='10s')
        view.wait_displayed()
        return view.read(widget_names=widget_names)

    def disable_recommendation(self, recommendation_name, system=False, hostname=None):
        """
        Disable a recommendation either for a specific system or entirely.

        :param recommendation_name: Name of the recommendation
        :param system: If True, disable for a specific system (requires hostname)
                    If False, disable the entire recommendation
        :param hostname: Required if system=True, hostname to disable for

        :return: View after recommendation is disabled
        """
        # Navigate to the Affected Systems details view
        view = self.navigate_to(self, 'Affected Systems', recommendation_name=recommendation_name)
        view.search_field.wait_displayed(timeout=10)
        if system:
            # Disable for a specific system
            if not hostname:
                raise ValueError('Hostname is required when system=True')
            view.search_field.fill(hostname)
            wait_for(lambda: view.table.row(name=hostname), handle_exception=True, timeout=20)
            time.sleep(15)
            kebab = view.table[0][5].widget
            kebab.item_select('Disable recommendation for system')
        else:
            view.actions.item_select('Disable recommendation')
        modal = DisableRecommendationModal(self.browser)
        wait_for(lambda: modal.is_displayed, handle_exception=True, timeout=10)
        modal.justification_note.fill('test')
        modal.save.click()
        wait_for(lambda: not modal.is_displayed, handle_exception=True, timeout=10)
        return view.read()

    def enable_recommendation(self, recommendation_name):
        """
        Re-enable a previously disabled recommendation.

        :param recommendation_name: Name of the recommendation

        :return: View after recommendation is enabled
        """
        # Navigate to All Recommendations page
        view = self.navigate_to(self, 'All Recommendations')

        self.browser.plugin.ensure_page_safe(timeout='10s')
        wait_for(lambda: view.table.is_displayed, timeout=20, handle_exception=True)
        view.clear_button.click()
        view.menu_toggle.fill('Status')
        view.menu_filter.fill('Disabled')
        self.browser.plugin.ensure_page_safe(timeout='10s')
        wait_for(lambda: view.table.is_displayed, timeout=20, handle_exception=True)
        view.table[0][7].widget.item_select('Enable recommendation')
        self.browser.plugin.ensure_page_safe(timeout='10s')
        return view.read()

    def read_no_authorized_message(self):
        view = self.navigate_to(self, 'All Recommendations')
        wait_for(lambda: view.title.is_displayed, timeout=30)
        wait_for(lambda: view.no_authorized_header.is_displayed, timeout=30)
        return view.no_authorized_header.read()


@navigator.register(RecommendationsTabEntity, 'Affected Systems')
class NavigateToAffectedSystems(NavigateStep):
    """Navigate from Recommendations tab to the Affected Systems details view."""

    VIEW = RecommendationsDetailsView

    def prerequisite(self, *args, **kwargs):
        # Ensure we are on the Recommendations tab first
        return self.navigate_to(self.obj, 'All Recommendations')

    def step(self, *args, **kwargs):
        recommendation_name = kwargs.get('recommendation_name')
        # Filter by recommendation name and open its expanded content
        time.sleep(5)
        self.parent.clear_button.click()
        self.parent.search_field.fill(recommendation_name)
        time.sleep(5)
        row, _ = wait_for(lambda: self.parent.table.row(name=recommendation_name), timeout=5)
        row.expand()
        row.content.affected_systems_url.click()


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


@navigator.register(RecommendationsTabEntity, 'All Recommendations')
class ShowRecommendationsView(NavigateStep):
    """Navigate to main Red Hat Lightspeed page"""

    VIEW = RecommendationsTabView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Recommendations')
