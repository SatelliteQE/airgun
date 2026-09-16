from wait_for import wait_for
from widgetastic.exceptions import RowNotFound
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox, Text, TextInput, View, Widget
from widgetastic_patternfly5 import (
    Button as PF5Button,
    ExpandableTable as PF5ExpandableTable,
    PatternflyTable as PF5PatternflyTable,
    Switch as PF5Switch,
)
from widgetastic_patternfly5.components.card import CardGroup
from widgetastic_patternfly5.components.menus.dropdown import Dropdown as PF5Dropdown
from widgetastic_patternfly5.components.table import PatternflyTableRow as PF5PatternflyTableRow
from widgetastic_patternfly5.components.tabs import Tab

from airgun.views.common import BaseLoggedInView, PF5WizardStepView


class ConditionalFilterToggle(Widget):
    """PF6 conditional filter dropdown toggle."""

    ROOT = './/button[@data-ouia-component-id="ConditionalFilterToggle"]'

    def read(self):
        """Return the currently selected filter label text."""
        self._switch_to_iframe()
        return self.browser.text(self)

    def _switch_to_iframe(self):
        """Ensure we're inside the compliance iframe."""
        driver = self.browser.selenium
        driver.switch_to.default_content()
        iframe = driver.find_element(
            'xpath', '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'
        )
        driver.switch_to.frame(iframe)

    def fill(self, item):
        """Select an item from the conditional filter dropdown."""
        self._switch_to_iframe()
        toggle = self.browser.selenium.find_element('xpath', self.ROOT)
        expanded = toggle.get_attribute('aria-expanded')
        if expanded != 'true':
            toggle.click()
        item_locator = f'.//li[@data-ouia-component-id="{item}"]//button'
        wait_for(
            lambda: self.browser.selenium.find_elements('xpath', item_locator),
            timeout=5,
            handle_exception=True,
        )
        self.browser.selenium.find_element('xpath', item_locator).click()


class ComplianceReportsView(BaseLoggedInView):
    """Main Insights Compliance Reports listing view."""

    FRAME = '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'

    title = Text('//h1[normalize-space(.)="Reports"]')
    filter_toggle = ConditionalFilterToggle()
    filter_input = TextInput(locator='.//input[@data-ouia-component-id="ConditionalFilter"]')

    reports_table = PF5PatternflyTable(
        locator='.//table[@data-ouia-component-id="ReportsTable"]',
        column_widgets={
            'Policy': Text('.//a'),
            'Operating system': Text('.//td[@data-label="Operating system"]'),
            'Systems meeting compliance': Text('.//td[@data-label="Systems meeting compliance"]'),
        },
    )

    # TODO: untested
    empty_state = Text('.//h5[contains(@class, "empty-state")]')

    @property
    def is_displayed(self):
        """Check that the view is displayed correctly."""
        return self.title.is_displayed


class ComplianceReportDetailsView(BaseLoggedInView):
    """Insights Compliance Report details view for a single policy report."""

    FRAME = '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'

    title = Text('//h1')
    # TODO: this should be a Breadcrumb component. Does one exist?
    breadcrumb = Text('.//nav[contains(@class, "breadcrumb")]')

    delete_report_button = PF5Button('Delete report')

    @View.nested
    class reporting(Tab):
        """Represents the `Reporting` Tab."""

        TAB_NAME = 'Reporting'
        TAB_LOCATOR = ParametrizedLocator(
            './/div[contains(@class, "-c-tabs")]/ul'
            '/li[button[@data-ouia-component-id={@tab_name|quote}]]'
        )
        ROOT = ParametrizedLocator('.//section[@data-ouia-component-id={@tab_name|quote}]')

        # TODO: not implemented yet
        systems_table = PF5PatternflyTable(
            locator='.//table[contains(@class, "pf-v6-c-table")]',
            column_widgets={
                'Name': Text('.//a'),
                'SSG version': Text('.//td[@data-label="SSG version"]'),
                'Failed rules': Text('.//td[@data-label="Failed rules"]'),
                'Compliance score': Text('.//td[@data-label="Compliance score"]'),
                'Last scanned': Text('.//td[@data-label="Last scanned"]'),
            },
        )

    @View.nested
    class never_reported(Tab):
        """Represents the `Never reported` Tab."""

        TAB_NAME = 'Never reported'
        TAB_LOCATOR = ParametrizedLocator(
            './/div[contains(@class, "-c-tabs")]/ul'
            '/li[button[@data-ouia-component-id={@tab_name|quote}]]'
        )
        ROOT = ParametrizedLocator('.//section[@data-ouia-component-id={@tab_name|quote}]')

        # TODO: not implemented yet
        systems_table = PF5PatternflyTable(
            locator='.//table[contains(@class, "pf-v6-c-table")]',
            column_widgets={
                'Name': Text('.//a'),
            },
        )

    @property
    def active_tab_name(self):
        """Return the name of the active Tab."""
        return self.active_tab.TAB_NAME

    @property
    def active_tab(self):
        """Return the currently active Tab view."""
        if self.reporting.is_active():
            return self.reporting
        return self.never_reported

    def switch_to_tab(self, tab_name):
        """Switch to the tab called `tab_name`."""
        for tab in [self.reporting, self.never_reported]:
            if tab_name == tab.TAB_NAME:
                tab.click()
                return

    @property
    def operating_system(self):
        """Returns the value of this report's systems OSs in a format 'RHEL 9, RHEL 10' etc."""
        return self.browser.text(
            './/dl/div[./dt[contains(normalize-space(.), "Operating system")]]/dd'
        )

    @property
    def threshold_value(self):
        """Returns the value of this report's Compliance threshold in a format '80.0%'."""
        return self.browser.text(
            './/dl/div[./dt[contains(normalize-space(.), "Compliance threshold")]]/dd'
        ).split(' ')[0]

    # TODO: once the systems tables are implemented, this should also check whether the active_tab is displayed
    @property
    def is_displayed(self):
        """Check whether the view is displayed."""
        return self.title.is_displayed and 'Report:' in self.title.text


class SCAPPoliciesTableRow(PF5PatternflyTableRow):
    """SCAP Policies table row with custom interactions."""

    def open(self):
        """Click the link that opens the Policy details view."""
        self.name.widget.click()


class SCAPPoliciesTable(PF5PatternflyTable):
    """SCAP Policies table with custom elements."""

    Row = SCAPPoliciesTableRow

    def row_by_name(self, policy_name):
        """Find the row object by name of policy."""
        for row in self.rows():
            if row.name.widget.text == policy_name:
                return row
        raise RowNotFound(f'Row named {policy_name} was not found.')

    def open_policy_details(self, policy_name):
        """Open the Policy details page."""
        self.row_by_name(policy_name).open()


class ScapPoliciesView(BaseLoggedInView):
    """Insights Compliance SCAP Policies listing view."""

    FRAME = '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'

    title = Text('//h1[normalize-space(.)="SCAP policies"]')
    search_input = TextInput(locator='.//input[@data-ouia-component-id="ConditionalFilter"]')
    create_policy = PF5Button(locator='.//button[@data-ouia-component-id="CreateNewPolicyButton"]')
    export_dropdown = PF5Dropdown(
        locator='.//div[contains(@class, "pf-v6-c-toolbar__item")][.//button[@aria-label="Export"]]'
    )
    actions_dropdown = PF5Dropdown(
        locator='.//div[contains(@class, "pf-v6-c-toolbar__item")]'
        '[.//button[@data-ouia-component-id="BulkActionsToggle"]]'
    )

    policies_table = SCAPPoliciesTable(
        locator='.//table[@data-ouia-component-id="PoliciesTable"]',
        column_widgets={
            'Name': Text('.//a'),
            'Operating system': Text('.//td[@data-label="Operating system"]'),
            'Systems': Text('.//td[@data-label="Systems"]'),
            'Business objective': Text('.//td[@data-label="Business objective"]'),
            'Compliance threshold': Text('.//td[@data-label="Compliance threshold"]'),
        },
    )

    @property
    def is_displayed(self):
        """Check that the view is displayed correctly."""
        return (
            self.title.is_displayed
            and self.policies_table.is_displayed
            and self.search_input.is_displayed
            and self.create_policy.is_displayed
        )

    def search(self, policy_name):
        """Filter policies by name."""
        self.search_input.fill(policy_name)

    def open_policy_details(self, policy_name):
        """Open policy details page of a specific policy."""
        self.policies_table.open_policy_details(policy_name)


class ScapPolicyDetailsView(BaseLoggedInView):
    """Insights Compliance SCAP Policy details view."""

    FRAME = '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'

    title = Text('//h1')
    # TODO: this should be a Breadcrumb component. Does one exist?
    breadcrumb = Text('.//nav[@data-ouia-component-id="PolicyDetailsPathBreadcrumb"]')

    @View.nested
    class details(Tab):
        """Details tab with policy metadata."""

        TAB_NAME = 'Details'
        ROOT = './/div[@data-ouia-component-id="PolicyDetailsCard"]'

        compliance_threshold = Text('.//h5[contains(., "Compliance threshold")]/following::p[1]')
        business_objective = Text('.//h5[contains(., "Business objective")]/following::p[1]')
        policy_description = Text('.//h5[contains(., "Policy description")]/following::p[1]')
        operating_system = Text('.//h5[contains(., "Operating system")]/following::p[1]')
        policy_type = Text('.//h5[contains(., "Policy type")]/following::p[1]')
        reference_id = Text('.//h5[contains(., "Reference ID")]/following::p[1]')

        @property
        def threshold_value(self):
            """Returns the value of this report's Compliance threshold in a format '80.0%'."""
            return self.compliance_threshold.text.split(' ')[0]

        @property
        def is_displayed(self):
            """Check whether the Tab is displayed."""
            return (
                self.compliance_threshold.is_displayed
                and self.business_objective.is_displayed
                and self.policy_description.is_displayed
                and self.operating_system.is_displayed
                and self.policy_type.is_displayed
                and self.reference_id.is_displayed
            )

    @View.nested
    class rules(Tab):
        """Rules tab with the list of SCAP rules."""

        TAB_NAME = 'Rules'
        ROOT = (
            './/section[contains(@class, "pf-v6-c-page__main-section")]'
            '[not(contains(@class, "pf-m-light"))]'
        )

        # TODO: not implemented yet
        rules_table = PF5PatternflyTable(
            locator='.//table[contains(@class, "pf-v6-c-table")]',
            column_widgets={
                'Name': Text('.//a'),
            },
        )

        @property
        def is_displayed(self):
            """Check whether the Tab is displayed."""
            return self.rules_table.is_displayed

    @View.nested
    class systems(Tab):
        """Systems tab with the list of associated systems."""

        TAB_NAME = 'Systems'
        ROOT = (
            './/section[contains(@class, "pf-v6-c-page__main-section")]'
            '[not(contains(@class, "pf-m-light"))]'
        )

        # TODO: not implemented yet
        systems_table = PF5PatternflyTable(
            locator='.//table[contains(@class, "pf-v6-c-table")]',
            column_widgets={
                'Name': Text('.//a'),
            },
        )

        @property
        def is_displayed(self):
            """Check whether the Tab is displayed."""
            return self.systems_table.is_displayed

    @property
    def active_tab_name(self):
        """Return the name of the active Tab."""
        return self.active_tab.TAB_NAME

    @property
    def active_tab(self):
        """Return the currently active Tab view."""
        for tab in [self.details, self.rules, self.systems]:
            if tab.is_active():
                return tab
        return self.details

    def switch_to_tab(self, tab_name):
        """Switch to the tab called `tab_name`."""
        for tab in [self.details, self.rules, self.systems]:
            if tab_name == tab.TAB_NAME:
                tab.click()
                return

    # TODO: once the tables are implemented, this should also check whether the active_tab is displayed
    @property
    def is_displayed(self):
        """Check whether the view is displayed."""
        return self.breadcrumb.is_displayed and self.active_tab.is_displayed


class CreatePolicyWizardView(BaseLoggedInView):
    """Wizard view for creating a new SCAP policy."""

    FRAME = '//iframe[contains(@class, "rh-cloud-insights-compliance-iframe")]'

    wizard_title = Text('.//div[contains(@class, "-c-wizard__header")]//h2')
    next_button = PF5Button('Next')
    back_button = PF5Button('Back')
    cancel_button = PF5Button('Cancel')
    finish_button = PF5Button('Finish')

    @View.nested
    class create_scap_policy(PF5WizardStepView):
        """Step 1: Select operating system and policy type."""

        name = 'Create SCAP policy'
        os_cards = CardGroup(locator='.//div[contains(@class, "pf-v6-l-flex")]')
        policy_type_table = PF5PatternflyTable(
            locator='.//table[@data-ouia-component-id="PolicyTypeTable"]',
            column_widgets={
                'Policy name': Text('.//td[@data-label="Policy name"]'),
                'Supported OS versions': Text('.//td[@data-label="Supported OS versions"]'),
            },
        )

        search_box = TextInput(
            locator=".//input[contains(@data-ouia-component-id, 'ConditionalFilter')]"
        )

        def search(self, policy_name):
            """Search the table by policy name."""
            self.search_box.fill(policy_name)

        @property
        def selected_os(self):
            """Return the title of the currently selected OS card, or None."""
            for card in self.os_cards:
                if 'pf-m-selected' in self.browser.get_attribute('class', card):
                    return card.title
            return None

        def select_os(self, os_name):
            """Select an operating system card by name (e.g. 'RHEL 9')."""
            for card in self.os_cards:
                if card.title == os_name:
                    card.browser.click(card)
                    return
            raise ValueError(
                f"OS card '{os_name}' not found. Available: {[card.title for card in self.os_cards]}"
            )

        def select_policy_type(self, policy_name):
            """Select a policy type by clicking its radio button."""
            self.search(policy_name)
            for row in self.policy_type_table.rows():
                if row['Policy name'].text == policy_name:
                    row[1].click()
                    return
            raise ValueError(f"Policy type '{policy_name}' not found")

        @property
        def is_displayed(self):
            """Check if the step is displayed."""
            return self.os_cards.is_displayed and (
                (not self.selected_os)
                or (self.search_box.is_displayed and self.policy_type_table.is_displayed)
            )

    @View.nested
    class details(PF5WizardStepView):
        """Step 2: Policy details."""

        policy_name = TextInput(id='name')
        reference_id = TextInput(id='refId')
        description = TextInput(id='description')
        compliance_threshold = TextInput(id='complianceThreshold')
        business_objective = TextInput(locator='.//input[contains(@id, "businessObjective")]')

        def change_policy_name(self, new_name):
            self.policy_name.fill(new_name)

        @property
        def is_displayed(self):
            """Check if the step is displayed."""
            return (
                self.policy_name.is_displayed
                and self.reference_id.is_displayed
                and self.description.is_displayed
                and self.compliance_threshold.is_displayed
                and self.business_objective.is_displayed
            )

    @View.nested
    class systems(PF5WizardStepView):
        """Step 3: Select systems."""

        # TODO: not implemented yet
        systems_table = PF5PatternflyTable(
            locator='.//table[contains(@class, "pf-v6-c-table")]',
            column_widgets={
                'Name': Text('.//a'),
            },
        )

        @property
        def is_displayed(self):
            """Check if the step is displayed."""
            # TODO: check systems_table once implemented
            return True

    @View.nested
    class rules(PF5WizardStepView):
        """Step 4: Select rules."""

        title = Text('.//h1[contains(@class, "pf-v6-c-content--h1")]')
        # TODO: define the other filters
        filter_toggle = ConditionalFilterToggle()
        filter_input = TextInput(locator='.//input[@data-ouia-component-id="ConditionalFilter"]')

        selected_only = PF5Switch(locator='.//label[contains(@class, "pf-v6-c-switch")]')
        # TODO: property that returns just the version
        ssg_version = Text('.//p[contains(., "SSG version")]')
        reset_to_default = Text('.//a[contains(., "Reset to default")]')
        view_policy_rules_link = Text('.//a[contains(., "View policy rules")]')
        list_view_button = PF5Button(locator='.//button[@aria-label="rows"]')
        tree_view_button = PF5Button(locator='.//button[@aria-label="tree"]')
        export_dropdown = PF5Dropdown(locator='.//button[@aria-label="Export"]/..')
        actions_dropdown = PF5Dropdown(locator='.//button[@aria-label="kebab dropdown toggle"]/..')
        rules_table = PF5ExpandableTable(
            locator='.//table[@aria-label="Rules Table"]',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//span[contains(@class, "pf-v6-c-table__text")]'),
                'Severity': Text('.//td[@data-label="Severity"]'),
                'Remediation type': Text('.//td[@data-label="Remediation type"]'),
            },
        )

        TAB_BUTTONS = './/div[@data-ouia-component-id="RHELVersions"]//button'

        @property
        def rhel_tabs(self):
            """Return list of available RHEL version tab names."""
            return [self.browser.text(t) for t in self.browser.elements(self.TAB_BUTTONS)]

        @property
        def active_rhel_tab(self):
            """Return the name of the currently active RHEL version tab."""
            el = self.browser.element(
                './/div[@data-ouia-component-id="RHELVersions"]'
                '//li[contains(@class, "pf-m-current")]//button'
            )
            return ' '.join(self.browser.text(el).split('\n')[0].strip().split(' ')[:2])

        def select_rhel_tab(self, tab_name):
            """Select a RHEL version tab (e.g. 'RHEL 8.0')."""
            for tab in self.browser.elements(self.TAB_BUTTONS):
                if tab_name in self.browser.text(tab):
                    tab.click()
                    return
            available = [
                ' '.join(self.browser.text(t).split(' ')[:2])
                for t in self.browser.elements(self.TAB_BUTTONS)
            ]
            raise ValueError(f"RHEL tab '{tab_name}' not found. Available: {available}")

        @property
        def is_displayed(self):
            """Check if the Step is displayed."""
            return (
                self.title.is_displayed
                and self.filter_toggle.is_displayed
                and self.filter_input.is_displayed
                and self.selected_only.is_displayed
                and self.ssg_version.is_displayed
                and self.reset_to_default.is_displayed
                and self.view_policy_rules_link.is_displayed
                and self.list_view_button.is_displayed
                and self.tree_view_button.is_displayed
                and self.export_dropdown.is_displayed
                and self.actions_dropdown.is_displayed
                and self.rules_table.is_displayed
            )

    @View.nested
    class review(PF5WizardStepView):
        """Step 5: Review policy configuration before creation."""

        title = Text('.//h1[contains(@class, "pf-v6-c-content--h1")]')
        description = Text('.//p[contains(@class, "pf-v6-c-content--p")]')
        policy_name = Text('.//h3')
        policy_type = Text('.//dt[contains(text(), "Policy type")]/following-sibling::dd[1]')
        compliance_threshold = Text(
            './/dt[contains(text(), "Compliance threshold")]/following-sibling::dd[1]'
        )
        systems_count = Text('.//dt[contains(text(), "Systems")]/following-sibling::dd[1]')
        os_versions = Text('.//dt[contains(text(), "RHEL OS Versions")]/following-sibling::dd[1]')

        @property
        def is_displayed(self):
            """Check if the Step is displayed."""
            return (
                self.title.is_displayed
                and self.description.is_displayed
                and self.policy_name.is_displayed
                and self.policy_type.is_displayed
                and self.compliance_threshold.is_displayed
                and self.systems_count.is_displayed
                and self.os_versions.is_displayed
            )

    @View.nested
    class finished(PF5WizardStepView):
        """Final step: Policy creation progress and completion."""

        title = Text('.//h1[contains(@class, "pf-v6-c-empty-state__title-text")]')
        progress_description = Text('.//div[contains(@class, "pf-v6-c-progress__description")]')
        progress_measure = Text('.//span[contains(@class, "pf-v6-c-progress__measure")]')
        error_message = Text('.//div[contains(@class, "wizard-failed-message")]')
        back_button = PF5Button(locator='.//button[@data-ouia-component-id="ReturnToAppButton"]')

        @property
        def is_error(self):
            """Check if the progress bar is in error/danger state."""
            progress = self.browser.element('.//div[contains(@class, "pf-v6-c-progress")]')
            return 'pf-m-danger' in self.browser.get_attribute('class', progress)

        @property
        def is_displayed(self):
            """Check if the finished step is displayed."""
            return (
                self.title.is_displayed
                and self.progress_description.is_displayed
                and self.progress_measure.is_displayed
                and self.back_button.is_displayed
            )

    NAV_LINK = './/button[contains(@class, "wizard__nav-link")]'
    STEPS = {
        'Create SCAP policy': 'create_scap_policy',
        'Details': 'details',
        'Systems': 'systems',
        'Rules': 'rules',
        'Review': 'review',
    }

    def next(self):
        """Advance to the next wizard step."""
        # TODO: check if the step has actually changed
        if self.next_button.is_enabled:
            self.next_button.click()

    def previous(self):
        """Go back to the previous wizard step."""
        # TODO: check if the step has actually changed
        if self.back_button.is_enabled:
            self.back_button.click()

    def finish(self):
        """Finish up policy creation."""
        # TODO: check if the step has actually changed
        if self.finish_button.is_enabled:
            self.finish_button.click()

    @property
    def active_step(self):
        """Return the view object of the currently active wizard step."""
        el = self.browser.element(
            './/button[contains(@class, "wizard__nav-link") and contains(@class, "pf-m-current")]'
        )
        step_name = self.browser.text(el)
        return getattr(self, self.STEPS[step_name])

    def skip_to_step(self, step_name):
        """Jump to a wizard step by clicking its nav link."""
        for el in self.browser.elements(self.NAV_LINK):
            if self.browser.text(el) == step_name:
                if self.browser.get_attribute('disabled', el) is not None:
                    raise ValueError(f"Wizard step '{step_name}' is disabled")
                el.click()
                return
        available = [self.browser.text(el) for el in self.browser.elements(self.NAV_LINK)]
        raise ValueError(f"Wizard step '{step_name}' not found. Available: {available}")

    @property
    def is_displayed(self):
        """Check whether the wizard is displayed."""
        return self.wizard_title.is_displayed
