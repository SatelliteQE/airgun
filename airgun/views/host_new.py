from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic.widget.table import Table
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import Pagination
from widgetastic_patternfly4 import Select
from widgetastic_patternfly4 import Tab
from widgetastic_patternfly4.ouia import BreadCrumb
from widgetastic_patternfly4.ouia import Button as OUIAButton
from widgetastic_patternfly4.ouia import ExpandableTable
from widgetastic_patternfly4.ouia import PatternflyTable

from airgun.views.common import BaseLoggedInView


class Card(View):
    """Each card in host view has it's own title with same locator"""

    title = Text('.//div[@class="pf-c-card__title"]')


class HostDetailsCard(Widget):
    """Details card body contains multiple host detail information"""

    LABELS = './/div[@class="pf-c-description-list__group"]//dt//span'
    VALUES = (
        './/div[@class="pf-c-description-list__group"]//dd//descendant::*/normalize-space(.)/..'
    )

    def read(self):
        """Return a dictionary where keys are property names and values are property values.
        Values are either in span elements or in div elements
        """
        items = {}
        labels = self.browser.elements(self.LABELS)
        values = self.browser.elements(self.VALUES)
        # the length of elements should be always same
        if len(values) != len(labels):
            raise AttributeError(
                'Each label should have one value, therefore length should be equal. '
                f'But length of labels: {len(labels)} is not equal to length of {len(values)}, '
                'Please double check xpaths.'
            )
        for key, value in zip(labels, values):
            value = self.browser.text(value)
            key = self.browser.text(key).replace(' ', '_').lower()
            items[key] = value
        return items


class NewHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb('OUIA-Generated-Breadcrumb-1')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.Overview.RecentJobsCard.is_table_loaded, exception=False
        )
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Hosts'

    edit = OUIAButton('OUIA-Generated-Button-secondary-1')
    dropdown = Dropdown(locator='//button[@id="hostdetails-kebab"]/..')

    @View.nested
    class Overview(Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class DetailsCard(Card):
            ROOT = './/article[.//div[text()="Details"]]'
            details = HostDetailsCard()

        @View.nested
        class HostStatusCard(Card):
            ROOT = './/article[.//span[text()="Host status"]]'
            status = Text('.//h4[contains(@data-ouia-component-id, "OUIA-Generated-Title")]')

            status_success = Text('.//span[span[@class="status-success"]]')
            status_warning = Text('.//span[span[@class="status-warning"]]')
            status_error = Text('.//span[span[@class="status-error"]]')
            status_disabled = Text('.//span[span[@class="disabled"]]')

        @View.nested
        class InstallableErrataCard(Card):
            ROOT = './/article[.//div[text()="Installable errata"]]'

            security_advisory = Text('.//a[contains(@href, "type=security")]')
            bug_fixes = Text('.//a[contains(@href, "type=bugfix")]')
            enhancements = Text('.//a[contains(@href, "type=enhancement")]')

        @View.nested
        class TotalRisksCard(Card):
            ROOT = './/article[.//div[text()="Total risks"]]'

            low = Text('.//*[@id="legend-labels-0"]/*')
            moderate = Text('.//*[@id="legend-labels-1"]/*')
            important = Text('.//*[@id="legend-labels-2"]/*')
            critical = Text('.//*[@id="legend-labels-3"]/*')

        @View.nested
        class RecentJobsCard(Card):
            ROOT = './/article[.//div[text()="Recent jobs"]]'
            is_table_loaded = './/ul[@aria-label="recent-jobs-table"]'

    @View.nested
    class Content(Tab):
        ROOT = './/div'

        @View.nested
        class Packages(Tab):
            ROOT = './/div[@id="packages-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = TextInput(locator='.//input[contains(@class, "pf-m-search")]')
            status_filter = Dropdown('.//div[@aria-label="select Status container"]/div')
            upgrade = Button('Upgrade')
            dropdown = Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = PatternflyTable(
                component_id="host-packages-table",
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Package': Text('./parent::td'),
                    'Status': Text('./span'),
                    'Installed version': Text('./parent::td'),
                    'Upgradable to': Text('./span'),
                    5: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                },
            )
            pagination = Pagination()

        @View.nested
        class Errata(Tab):
            ROOT = './/div[@id="errata-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = TextInput(locator='.//input[contains(@class, "pf-m-search")]')
            type_filter = Select(locator='.//div[@aria-label="select Type container"]/div')
            severity_filter = Select(locator='.//div[@aria-label="select Severity container"]/div')
            apply = Button('Apply')
            dropdown = Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = ExpandableTable(
                component_id="host-errata-table",
                column_widgets={
                    1: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Errata': Text('./a'),
                    'Type': Text('./span'),
                    'Severity': Text('./span'),
                    'Installable': Text('./span'),
                    'Synopsis': Text('./span'),
                    'Published date': Text('./span/span'),
                    8: Dropdown(locator='./div'),
                },
            )
            pagination = Pagination()

        @View.nested
        class ModuleStreams(Tab):
            TAB_NAME = 'Module streams'
            ROOT = './/div[@id="modulestreams-tab"]'

            searchbar = TextInput(locator='.//input[contains(@class, "pf-m-search")]')
            status_filter = Select(locator='.//div[@aria-label="select Status container"]/div')
            installation_status_filter = Select(
                locator='.//div[@aria-label="select Installation status container"]/div'
            )
            dropdown = Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = Table(
                locator='.//table[@aria-label="Content View Table"]',
                column_widgets={
                    'Name': Text('./a'),
                    'State': Text('.//span'),
                    'Stream': Text('./parent::td'),
                    'Installation status': Text('.//small'),
                    'Installed profile': Text('./parent::td'),
                    5: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                },
            )
            pagination = Pagination()

        @View.nested
        class RepositorySets(Tab):
            TAB_NAME = 'Repository sets'
            ROOT = './/div[@id="repo-sets-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = TextInput(locator='.//input[contains(@class, "pf-m-search")]')
            status_filter = Select(locator='.//div[@aria-label="select Status container"]/div')
            dropdown = Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = Table(
                locator='.//table[@aria-label="Content View Table"]',
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Repository': Text('./span'),
                    'Product': Text('./a'),
                    'Repository path': Text('./span'),
                    'Status': Text('.//span[contains(@class, "pf-c-label__content")]'),
                    5: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                },
            )
            pagination = Pagination()

    @View.nested
    class Traces(Tab):
        enable_traces = OUIAButton('OUIA-Generated-Button-primary-1')

    @View.nested
    class Ansible(Tab):
        pass

    @View.nested
    class Insights(Tab):
        pass


class InstallPackagesView(View):
    """Install packages modal"""

    ROOT = './/div[@id="package-install-modal"]'

    select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
    searchbar = TextInput(locator='.//input[contains(@class, "pf-m-search")]')

    table = Table(
        locator='.//table[@aria-label="Content View Table"]',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Package': Text('./parent::td'),
            'Version': Text('./parent::td'),
        },
    )
    pagination = Pagination()

    install = Button(locator='.//button[(normalize-space(.)="Install")]')
    cancel = Button('Cancel')
