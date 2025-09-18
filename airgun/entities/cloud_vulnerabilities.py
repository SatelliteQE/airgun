from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_vulnerabilities import CloudVulnerabilityView, CVEDetailsView
from airgun.views.host_new import NewHostDetailsView


class CloudVulnerabilityEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_vulnerability'

    def read(self, entity_name=None, widget_names=None):
        view = self.navigate_to(self, 'All')
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)
        return view.vulnerabilities_table.read()

    def _navigate_to_cve_details(self, cve_id):
        """Helper method to navigate to CVE details page"""
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        wait_for(lambda: view.vulnerabilities_table.is_displayed, timeout=30)
        view.search_bar.fill(cve_id)
        view.browser.element(f'.//a[contains(@href, "{cve_id}")]').click()

    def get_cve_details(self, cve_id):
        """
        Read CVE details from CVE details page

        Args:
            cve_id (str): CVE ID to get details
        """
        self._navigate_to_cve_details(cve_id)
        view = CVEDetailsView(self.browser)
        return view.read()

    def get_affected_hosts_by_cve(self, cve_id):
        """
        Get list of affected hosts for a specific CVE

        Args:
            cve_id (str): CVE ID to get affected hosts for
        """
        self._navigate_to_cve_details(cve_id)
        cve_details_view = CVEDetailsView(self.browser)
        wait_for(lambda: cve_details_view.affected_hosts_table.is_displayed, timeout=30)
        return cve_details_view.affected_hosts_table.read()

    def validate_cve_to_host_details_flow(self, cve_id, hostname=None):
        """
        Complete flow: CVE details -> affected hosts -> click host -> host details page

        Args:
            cve_id (str): CVE ID to test
            hostname (str, optional): Specific host name to click on.
        """
        self._navigate_to_cve_details(cve_id)
        cve_details_view = CVEDetailsView(self.browser)
        wait_for(lambda: cve_details_view.affected_hosts_table.is_displayed, timeout=30)
        cve_details_view.search_bar.fill(hostname)
        cve_details_view.browser.element(f'.//a[contains(text(), "{hostname}")]').click()
        host_details_view = NewHostDetailsView(self.browser)
        host_details_view.breadcrumb.wait_displayed()
        wait_for(
            lambda: host_details_view.vulnerabilities.vulnerabilities_table.is_displayed, timeout=30
        )
        vulnerabilities = getattr(host_details_view.vulnerabilities, 'vulnerabilities_table', None)
        if vulnerabilities is not None:
            return vulnerabilities.read()
        else:
            return []


@navigator.register(CloudVulnerabilityEntity, 'All')
class ShowVulnerabilityListView(NavigateStep):
    """Navigate to main Red Hat Lightspeed -> Vulnerability page"""

    VIEW = CloudVulnerabilityView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Vulnerability')
