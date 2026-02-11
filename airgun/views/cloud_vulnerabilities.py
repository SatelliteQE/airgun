from widgetastic.widget import Checkbox, Select, Text, TextInput, Widget
from widgetastic_patternfly5 import (
    Button as PF5Button,
    ExpandableTable as PF5OUIAExpandableTable,
    Modal as PF5Modal,
    Pagination as PF5Pagination,
    PatternflyTable as PF5OUIAPatternflyTable,
)

from airgun.views.common import BaseLoggedInView
from airgun.views.host_new import PF5CheckboxTreeView
from airgun.widgets import SearchInput


class EditBusinessRiskModal(PF5Modal):
    """Modal for editing CVE business risk (single or bulk)."""

    ROOT = './/div[@data-ouia-component-id="edit-cve-business-risk-modal"]'

    title = Text('.//h1[contains(@class, "pf-v5-c-modal-box__title")]')
    selection_text = Text('.//div[contains(@class, "pf-v5-c-modal-box__body")]//p')

    # Radio buttons for business risk levels (using input name attribute)
    critical = Checkbox(locator='.//input[@name="Critical"]')
    high = Checkbox(locator='.//input[@name="High"]')
    medium = Checkbox(locator='.//input[@name="Medium"]')
    low = Checkbox(locator='.//input[@name="Low"]')
    not_defined = Checkbox(locator='.//input[@name="Not defined"]')

    justification_note = TextInput(locator='.//textarea[@aria-label="justification note"]')

    save = PF5Button('Save')
    cancel = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class EditStatusModal(PF5Modal):
    """Modal for editing CVE status (single or bulk)."""

    ROOT = './/div[@data-ouia-component-id="editCveStatusModal"]'

    title = Text('.//h1[contains(@class, "pf-v5-c-modal-box__title")]')
    selection_text = Text('.//div[contains(@class, "pf-v5-c-modal-box__body")]//p')

    # Dropdown for status options
    status_select = Select(locator='.//select')

    justification_note = TextInput(locator='.//textarea[@aria-label="justification note"]')
    no_overwrite = Checkbox(locator='.//input[@id="overwrite-checkbox"]')

    save = PF5Button('Save')
    cancel = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class BulkActionsMenu(Widget):
    """Bulk actions kebab menu for selected CVEs."""

    ROOT = './/button[@data-ouia-component-id="BulkActionsToggle"]'

    def item_select(self, item):
        """Open the bulk actions menu and click an item."""
        # Click the toggle button
        self.browser.click(self)

        # Wait for menu to appear and click the item
        # Use absolute XPath since menu is dynamically positioned in the document
        item_locator = f'//div[contains(@class, "pf-v5-c-menu")]//span[contains(@class, "pf-v5-c-menu__item-text") and contains(text(), "{item}")]'
        self.browser.click(item_locator)


class RowActionsMenu(Widget):
    """Row kebab menu for individual CVE actions."""

    ROOT = './/button[@aria-label="Kebab toggle"]'

    def read(self):
        """This column doesn't have readable data."""
        return None

    def item_select(self, item):
        """Open the kebab menu and click an item."""
        # Click the kebab button (this widget's root element)
        self.browser.click(self)

        # Wait for menu to appear and click the item
        # The menu appears as a sibling of the button in the parent <td>
        # Search from parent to find the menu
        item_locator = f'//div[contains(@class, "pf-v5-c-menu")]//span[contains(@class, "pf-v5-c-menu__item-text") and contains(text(), "{item}")]'
        self.browser.click(item_locator)


class FilterTypeMenu(Widget):
    """Dropdown for selecting the type of filter (e.g., 'Applies to OS')"""

    ROOT = './/button[@aria-label="Conditional filter toggle"]'

    def item_select(self, item):
        """Open the filter type menu and click an item."""
        # Click the toggle button
        self.browser.click(self)

        # Wait for menu to appear and click the item (search from document root)
        item_locator = f'//div[contains(@class, "pf-v5-c-menu")]//span[contains(@class, "pf-v5-c-menu__item-text") and contains(text(), "{item}")]'
        self.browser.click(item_locator)


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
    no_cves_found_message = Text('.//h5[contains(@class, "pf-v5-c-empty-state__title-text")]')

    # OS Filter widgets
    # Multi-step conditional filter:
    # 1. Select "Applies to OS" from filter_type_menu
    # 2. Click the os_filter_button to open the dropdown
    # 3. Select OS versions from the os_filter_tree (TreeView with checkboxes)
    filter_type_menu = FilterTypeMenu()
    os_filter_button = PF5Button(locator='.//button[@aria-label="Group filter"]')
    os_filter_tree = PF5CheckboxTreeView(locator='.//div[@class="pf-v5-c-tree-view"]')

    # Bulk actions menu
    bulk_actions = BulkActionsMenu()

    # Modals
    edit_business_risk_modal = EditBusinessRiskModal()
    edit_status_modal = EditStatusModal()

    vulnerabilities_table = PF5OUIAExpandableTable(
        # component_id='OUIA-Generated-Table-1',
        locator='.//table[contains(@class, "pf-v5-c-table")]',
        column_widgets={
            0: Checkbox(locator='.//label/input[@type="checkbox"]'),
            1: PF5Button(locator='.//button[@aria-label="Details"]'),
            'CVE ID': Text('.//td[@data-label="CVE ID"]'),
            'Publish date': Text('.//td[@data-label="Publish date"]'),
            'Severity': Text('.//td[@data-label="Severity"]'),
            'CVSS base score': Text('.//td[@data-label="CVSS base score"]'),
            'Affected hosts': Text('.//td[@data-label="Affected hosts"]'),
            'Business risk': Text('.//td[@data-label="Business risk"]'),
            'Status': Text('.//td[@data-label="Status"]'),
            'Column with row actions': RowActionsMenu(),
        },
    )
    pagination = PF5Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ActionsDropdownMenu(Widget):
    """Actions dropdown menu on CVE details page."""

    ROOT = './/button[@data-testid="dropdown-toggle"]'

    def item_select(self, item):
        """Open the actions dropdown and click an item."""
        # Click the toggle button
        self.browser.click(self)

        # Wait for menu to appear and click the item
        # Use absolute XPath since menu is dynamically positioned in the document
        item_locator = f'//div[contains(@class, "pf-v5-c-menu")]//span[contains(@class, "pf-v5-c-menu__item-text") and contains(text(), "{item}")]'
        self.browser.click(item_locator)


class CVEDetailsView(BaseLoggedInView):
    """Class that describes the Vulnerabilities Details page"""

    title = Text('.//h1[@data-ouia-component-type="RHI/Header"]')
    description = Text('.//div[@class="pf-v5-c-content"]')
    search_bar = SearchInput(locator='.//input[contains(@aria-label, "search-field")]')

    # Actions dropdown
    actions_dropdown = ActionsDropdownMenu()

    # Modals (shared with main view)
    edit_business_risk_modal = EditBusinessRiskModal()
    edit_status_modal = EditStatusModal()

    affected_hosts_table = PF5OUIAPatternflyTable(
        # component_id='OUIA-Generated-Table-1',
        locator='.//table[contains(@class, "pf-v5-c-table")]',
        column_widgets={
            'Name': Text('./a'),
            'OS': Text('.//td[contains(@data-label, "OS")]'),
            'Last seen': Text('.//td[contains(@data-label, "Last seen")]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
