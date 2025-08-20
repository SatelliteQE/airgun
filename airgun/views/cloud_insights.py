from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Pagination as PF5Pagination,
    Title as PF5Title,
)
from widgetastic_patternfly5.ouia import (
    Dropdown as PF5OUIADropdown,
    Modal as PF5OUIAModal,
    PatternflyTable as PF5OUIAPatternflyTable,
    Switch as PF5OUIASwitch,
    Text as PF5Text,
    ExpandableTable as PF5ExpandableTable,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4

class CloudTokenView(BaseLoggedInView):
    """Red Hat Lightspeed Landing page for adding RH Cloud Token."""

    rhcloud_token = TextInput(locator='//input[contains(@aria-label, "input-cloud-token")]')
    save_token = PF5Button('Save setting and sync recommendations')

    @property
    def is_displayed(self):
        return self.rhcloud_token.wait_displayed()


class RemediationView(PF5OUIAModal):
    """Red Hat Lightspeed Remediations modal view"""

    OUIA_ID = 'remediation-modal'
    remediate = PF5Button('Remediate')
    cancel = PF5Button('Cancel')
    table = PF5OUIAPatternflyTable(
        component_id='remediations-table',
        column_widgets={
            'Hostname': Text('./a'),
            'Recommendation': Text('./a'),
            'Resolution': Text('.//a'),
            'Reboot Required': Text('.//a'),
        },
    )

    @property
    def is_displayed(self):
        return self.title.wait_displayed()


class CloudInsightsView(BaseLoggedInView, SearchableViewMixinPF4):
    """Main Red Hat Lightspeed view."""

    title = Text('//h1[normalize-space(.)="Red Hat Lightspeed"]')
    insights_sync_switcher = PF5OUIASwitch('foreman-rh-cloud-switcher')
    remediate = PF5Button('Remediate')
    insights_dropdown = PF5OUIADropdown('title-dropdown')
    select_all = Checkbox(locator='.//input[@aria-label="Select all rows"]')
    table = PF5OUIAPatternflyTable(
        component_id='rh-cloud-recommendations-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Hostname': Text('.//a'),
            'Recommendation': Text('.//a'),
            'Total Risk': Text('.//a'),
            'Playbook': Text('.//a'),
        },
    )
    select_all_hits = PF5Button('Select recommendations from all pages')
    clear_hits_selection = PF5Button('Clear Selection')
    pagination = PF5Pagination()
    remediation_window = View.nested(RemediationView)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None



class RecommendationsDetails(View):
    """Models everything in the recommendations details views execpt the affected system link
    """

    pass

class RecommendationsTableExpandedRowView(RecommendationsDetails, View):
    """View that models the recommendation expandable row content"""

    affected_systems_url = Text(
        locator=".//*[contains(@class, 'ins-c-rule-details__view-affected')]//a"
    )

    @property
    def is_displayed(self):
        """Check that the row is displayed."""
        return self.affected_systems_url.is_displayed


class RecommendationsTabView(BaseLoggedInView):
    """View representing the Recommendations Tab."""

    #disable_recommendation_modal = View.nested(DisableRecommendationModal)
    title = PF5Title('Recommendations')
    search_field = TextInput(locator=(".//input[@aria-label='text input']"))
    clear_button = PF5Button("Reset Filters")
    # incidents = PF5Text(component_id='Incidents')
    # critical_recommendations = PF5Text(component_id='Critical recommendations')
    # important_recommendations = PF5Text(component_id='Important recommendations')
    conditional_filter_dropdown = PF5OUIADropdown(component_id = 'ConditionalFilter')
    #export_dropdown = Dropdown(locator=".//*[contains(@aria-label, 'Export')]/..")
    #reset_filters_button = Button("Reset filters")
    #include_disabled_recommendations_button = PF5Button("Include disabled recommendations")
    # upper_pagination = CompactPagination(
    #     locator=".//*[contains(@data-ouia-component-id, 'CompactPagination')]"
    # )
    #lower_pagination = Pagination(locator=".//*[contains(@class, '-m-bottom')]")

    table = PF5ExpandableTable(
        #locator='.//table[contains(@aria-label, "rule-table")]',
        content_view=RecommendationsTableExpandedRowView,
        component_id='OUIA-Generated-Table-3',
        column_widgets={
            "Name": Text(".//a"),
            "Modified": Text(".//span"),
            "Category": Text(".//span"),
            "Total risk": Text(".//span"),
            "Systems": Text(".//div"),
            "Remediation type": Text(".//span"),
        },
    )

    @property
    def is_empty(self):
        """Check whether the table is empty."""
        return self.include_disabled_recommendations_button.is_displayed


    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class RecommendationsDetailsView(SearchableViewMixinPF4, RecommendationsDetails):
    """Modify affected system table here to apply remediations"""
    pass
