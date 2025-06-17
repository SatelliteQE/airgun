from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView


class CloudVulnerabilityView(BaseLoggedInView):
    """Main Insights Vulnerabilities view."""

    title = Text('//h1[normalize-space(.)="Vulnerabilities"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
