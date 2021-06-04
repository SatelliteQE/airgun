from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.cloud_insights import CloudInsightsView
from airgun.views.job_invocation import JobInvocationCreateView


class CloudInsightsEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_cloud'

    def search(self, value):
        """Search for 'query' and return hostname/recommendation names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        view.search(value)
        return view.recommendation_table.read()

    def remediate(self, entity_name):
        """Remediate hosts based on search input."""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.select_all.fill(True)
        view.select_all_hits.click()
        view.remediate.click()
        view.remediation_window.remediate.click()
        self.run_job()

    def sync_hits(self):
        """Sync RH Cloud - Insights recommendations."""
        view = self.navigate_to(self, 'All')
        view.start_hits_sync.click()

    def read(self, widget_names=None):
        """Read all values for created activation key entity"""
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

    def run_job(self):
        """Run remediation job"""
        view = self.navigate_to(self, 'Run')
        self.browser.plugin.ensure_page_safe(timeout='60s')
        view.submit.click()


@navigator.register(CloudInsightsEntity, 'All')
class ShowCloudInsightsView(NavigateStep):
    """Navigate to main Red Hat Insights page"""

    VIEW = CloudInsightsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Insights')


@navigator.register(CloudInsightsEntity, 'Run')
class RunJob(NavigateStep):
    """Navigate to Job Invocation screen."""

    VIEW = JobInvocationCreateView
