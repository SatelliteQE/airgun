from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_vulnerabilities import CloudVulnerabilityView, CVEDetailsView


class CloudVulnerabilityEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_vulnerability'

    def read(self, entity_name=None, widget_names=None):
        view = self.navigate_to(self, 'All')
        return view.vulnerabilities_table.read()

    def get_cve_details(self, cve_id):
        """
        Read CVE details from CVE details page

        Args:
            cve_id (str): CVE ID to get details
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.search_bar.fill(cve_id)
        view.vulnerabilities_table.row(cve_id)['CVE ID'].click()
        view = CVEDetailsView(self.browser)
        return view.read()


@navigator.register(CloudVulnerabilityEntity, 'All')
class ShowVulnerabilityListView(NavigateStep):
    """Navigate to main Red Hat Lightspeed -> Vulnerability page"""

    VIEW = CloudVulnerabilityView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Vulnerability')
