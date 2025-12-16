from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly5 import (
    Button as PF5Button,
    ExpandableTable as PF5ExpandableTable,
    Menu as PF5Menu,
    Pagination as PF5Pagination,
    PatternflyTable as PF5Table,
    Select as PF5Select,
    Title as PF5Title,
)
from widgetastic_patternfly5.ouia import (
    Dropdown as PF5OUIADropdown,
    Modal as PF5OUIAModal,
    PatternflyTable as PF5OUIAPatternflyTable,
    Switch as PF5OUIASwitch,
    TextInput as PF5OUIATextInput,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4, TableRowKebabMenu


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


class BulkSelectMenuToggle(PF5Menu):
    """
    A menu toggle component that combines a checkbox with a dropdown menu.
    Used for bulk selection operations with additional menu options.
    Usage example (view.bulk_select = BulkSelectMenuToggle()):
    view.bulk_select.select_all() -> to select all items using the checkbox
    view.bulk_select.deselect_all() -> to deselect all items using the checkbox
    view.bulk_select.is_all_selected -> to check if all items are selected
    view.bulk_select.items -> to access the menu items
    (['Select none', 'Select page (1 items)', 'Select all (1 items)'])
    view.bulk_select.item_select('Select none') -> to select a specific item by name
    """

    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = './/button[@data-ouia-component-id="BulkSelect"]'
    ROOT = f'{BUTTON_LOCATOR}/..'
    ITEMS_LOCATOR = './/ul[contains(@class, "pf-v5-c-menu__list")]/li'
    ITEM_LOCATOR = (
        '//*[contains(@class, "pf-v5-c-menu__item") and .//*[contains(normalize-space(.), {})]]'
    )
    # Checkbox element within the menu toggle
    checkbox = Checkbox(locator='.//input[@data-ouia-component-id="BulkSelectCheckbox"]')

    def select_all(self):
        """Select all items using the checkbox."""
        if not self.checkbox.selected:
            self.checkbox.click()

    def deselect_all(self):
        """Deselect all items using the checkbox."""
        if self.checkbox.selected:
            self.checkbox.click()

    @property
    def is_all_selected(self):
        """Return True if the select all checkbox is checked."""
        return self.checkbox.selected


class MenuToggleSelectParamLocator(PF5Select):
    """
    Inherit MenuToggleSelect and set ROOT to the default locator.
    """

    BUTTON_LOCATOR = './/button[contains(@class, "pf-v5-c-menu-toggle")]'
    DEFAULT_LOCATOR = (
        './/div[contains(@class, "pf-v5-c-menu") and @data-ouia-component-type="PF5/Select"]'
    )
    ROOT = ParametrizedLocator('{@locator}/..')
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-v5-c-menu__list')]/li"
    ITEM_LOCATOR = (
        "//*[contains(@class, 'pf-v5-c-menu__item') and .//*[contains(normalize-space(.), {})]]"
    )


class RemediateSummary(PF5OUIAModal):
    """Models the Remediation summary page and button"""

    title = PF5Title('Remediation summary')
    remediate = PF5Button('Remediate')


class DisableRecommendationModal(PF5OUIAModal):
    """"""

    checkbox = Checkbox(locator='.//input[@type="checkbox"]')
    justification_note = TextInput(locator=".//input[contains(@id, 'disable-rule-justification')]")
    save = PF5Button('Save')
    cancel = PF5Button('Cancel')


class RecommendationsDetailsView(BaseLoggedInView):
    """Models everything in the recommendations details views execpt the affected system link"""

    title = PF5Title('Affected Systems')
    clear_button = PF5Button('Reset filters')
    remediate = PF5Button('Remediate')
    download_playbook = PF5Button('Download playbook')
    enable_recommendation = PF5Button('Enable recommendation')
    view_systems = PF5Button('View systems')
    search_field = TextInput(locator=('.//input[@aria-label="text input"]'))
    bulk_select = BulkSelectMenuToggle()
    table = PF5Table(
        locator='.//table[contains(@aria-label, "Host inventory")]',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text('.//a'),
            'OS': Text('.//span'),
            'Last seen': Text('.//span'),
            'First impacted': Text('.//span'),
            5: TableRowKebabMenu(),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.table, exception=False) is not None


class RecommendationsTableExpandedRowView(RecommendationsDetailsView):
    """View that models the recommendation expandable row content"""

    affected_systems_url = Text(
        locator='.//*[contains(@class, "ins-c-rule-details__view-affected")]//a'
    )

    @property
    def is_displayed(self):
        """Check that the row is displayed."""
        return self.affected_systems_url.is_displayed


class RecommendationsTabView(BaseLoggedInView):
    """View representing the Recommendations Tab."""

    title = PF5Title('Recommendations')
    search_field = TextInput(locator=('.//input[@aria-label="text input"]'))
    clear_button = PF5Button('Reset filters')
    incidents = Text(locator='.//a[@data-testid="Incidents"]')
    critical_recommendations = Text(locator='.//a[@data-testid="Critical recommendations"]')
    important_recommendations = Text(locator='.//a[@data-testid="Important recommendations"]')
    conditional_filter_dropdown = PF5OUIATextInput('ConditionalFilter')
    menu_toggle = MenuToggleSelectParamLocator(
        locator='.//button[@data-ouia-component-id="ConditionalFilterToggle"]'
    )
    menu_filter = MenuToggleSelectParamLocator(locator='.//button[@aria-label="Options menu"]')
    table = PF5ExpandableTable(
        locator='.//table[contains(@data-ouia-component-id, "rules-table")]',
        content_view=RecommendationsTableExpandedRowView,
        column_widgets={
            'Name': Text('.//a'),
            'Modified': Text('.//span'),
            'Category': Text('.//span'),
            'Total risk': Text('.//span'),
            'Systems': Text('.//div'),
            'Remediation type': Text('.//span'),
            6: TableRowKebabMenu(),
        },
    )

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.table, exception=False) is not None
            and self.browser.wait_for_element(self.clear_button, exception=False) is not None
        )
