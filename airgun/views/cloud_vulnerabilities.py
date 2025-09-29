from widgetastic.widget import Text

# from widgetastic_patternfly5.ouia import (
#     ExpandableTable as PF5OUIAExpandableTable,
#     PatternflyTable as PF5OUIAPatternflyTable,
# )
from widgetastic_patternfly5 import (
    Button as PF5Button,
    ExpandableTable as PF5OUIAExpandableTable,
    Pagination as PF5Pagination,
    PatternflyTable as PF5OUIAPatternflyTable,
)

from airgun.views.common import BaseLoggedInView
from airgun.widgets import SearchInput


class CloudVulnerabilityView(BaseLoggedInView):
    """Main Insights Vulnerabilities view."""

    title = Text('//h1[normalize-space(.)="Vulnerabilities"]')
    cves_with_known_exploits_card = PF5Button(
        '//div[@data-ouia-component-type="PF5/Card"][.//b[text()="CVEs with known exploits"]]'
    )
    cves_with_security_rules_card = PF5Button(
        '//div[@data-ouia-component-type="PF5/Card"][.//b[text()="CVEs with security rules"]]'
    )
    cves_with_critical_severity_card = PF5Button(
        '//div[@data-ouia-component-type="PF5/Card"][.//b[text()="CVEs with critical severity"]]'
    )
    cves_with_important_severity_card = PF5Button(
        '//div[@data-ouia-component-type="PF5/Card"][.//b[text()="CVEs with important severity"]]'
    )
    search_bar = SearchInput(locator='.//input[contains(@aria-label, "search-field")]')
    cve_menu_toggle = PF5Button('.//button[contains(@class, "pf-v5-c-menu-toggle")]')
    no_cves_found_message = Text(
        './/h5[contains(@class, "pf-v5-c-empty-state__title-text")]'
    )

    vulnerabilities_table = PF5OUIAExpandableTable(
        # component_id='OUIA-Generated-Table-1',
        locator='.//table[contains(@class, "pf-v5-c-table")]',
        column_widgets={
            0: PF5Button(locator='.//button[@aria-label="Details"]'),
            "CVE ID": Text('.//td[@data-label="CVE ID"]'),
            "Publish date": Text('.//td[@data-label="Publish date"]'),
            "Severity": Text('.//td[@data-label="Severity"]'),
            "CVSS base score": Text('.//td[@data-label="CVSS base score"]'),
            "Affected hosts": Text('.//td[@data-label="Affected hosts"]'),
        },
    )
    pagination = PF5Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class CVEDetailsView(BaseLoggedInView):
    """Class that describes the Vulnerabilities Details page"""

    title = Text('.//h1[@data-ouia-component-type="RHI/Header"]')
    description = Text('.//div[@class="pf-v5-c-content"]')
    search_bar = SearchInput(locator='.//input[contains(@aria-label, "search-field")]')
    affected_hosts_table = PF5OUIAPatternflyTable(
        # component_id='OUIA-Generated-Table-1',
        locator='.//table[contains(@class, "pf-v5-c-table")]',
        column_widgets={
            "Name": Text("./a"),
            "OS": Text('.//td[contains(@data-label, "OS")]'),
            "Last seen": Text('.//td[contains(@data-label, "Last seen")]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
