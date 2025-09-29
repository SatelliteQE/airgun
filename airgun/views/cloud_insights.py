from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Pagination as PF5Pagination,
)
from widgetastic_patternfly5.ouia import (
    Dropdown as PF5OUIADropdown,
    Modal as PF5OUIAModal,
    PatternflyTable as PF5OUIAPatternflyTable,
    Switch as PF5OUIASwitch,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class CloudTokenView(BaseLoggedInView):
    """Red Hat Lightspeed Landing page for adding RH Cloud Token."""

    rhcloud_token = TextInput(
        locator='//input[contains(@aria-label, "input-cloud-token")]'
    )
    save_token = PF5Button("Save setting and sync recommendations")

    @property
    def is_displayed(self):
        return self.rhcloud_token.wait_displayed()


class RemediationView(PF5OUIAModal):
    """Red Hat Lightspeed Remediations modal view"""

    OUIA_ID = "remediation-modal"
    remediate = PF5Button("Remediate")
    cancel = PF5Button("Cancel")
    table = PF5OUIAPatternflyTable(
        component_id="remediations-table",
        column_widgets={
            "Hostname": Text("./a"),
            "Recommendation": Text("./a"),
            "Resolution": Text(".//a"),
            "Reboot Required": Text(".//a"),
        },
    )

    @property
    def is_displayed(self):
        return self.title.wait_displayed()


class CloudInsightsView(BaseLoggedInView, SearchableViewMixinPF4):
    """Main Red Hat Lightspeed view."""

    title = Text('//h1[normalize-space(.)="Red Hat Lightspeed"]')
    insights_sync_switcher = PF5OUIASwitch("foreman-rh-cloud-switcher")
    remediate = PF5Button("Remediate")
    insights_dropdown = PF5OUIADropdown("title-dropdown")
    select_all = Checkbox(locator='.//input[@aria-label="Select all rows"]')
    table = PF5OUIAPatternflyTable(
        component_id="rh-cloud-recommendations-table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            "Hostname": Text(".//a"),
            "Recommendation": Text(".//a"),
            "Total Risk": Text(".//a"),
            "Playbook": Text(".//a"),
        },
    )
    select_all_hits = PF5Button("Select recommendations from all pages")
    clear_hits_selection = PF5Button("Clear Selection")
    pagination = PF5Pagination()
    remediation_window = View.nested(RemediationView)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
