from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_vulnerabilities import CloudVulnerabilityView


class CloudVulnerabilityEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/insights_vulnerability'

    def read(self, entity_name=None, widget_names=None):
        view = self.navigate_to(self, 'All')
        result = view.read(widget_names=widget_names)
        return result


@navigator.register(CloudVulnerabilityEntity, 'All')
class ShowVulnerabilityListView(NavigateStep):
    """Navigate to main Red Hat Lightspeed -> Vulnerability page"""

    VIEW = CloudVulnerabilityView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Red Hat Lightspeed', 'Vulnerability')
