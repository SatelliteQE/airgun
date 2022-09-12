import time

from selenium.webdriver.common.keys import Keys
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
from widgetastic_patternfly4 import PatternflyTable
from widgetastic_patternfly4.ouia import BreadCrumb
from widgetastic_patternfly4.ouia import Button as OUIAButton
from widgetastic_patternfly4.ouia import ExpandableTable
from widgetastic_patternfly4.ouia import PatternflyTable

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.widgets import Pf4ActionsDropdown
from airgun.widgets import Pf4ConfirmationDialog
from airgun.widgets import SatTableWithoutHeaders


class SearchInput(TextInput):
    def fill(self, value):
        changed = super().fill(value)
        if changed:
            # workaround for BZ #2140636
            time.sleep(1)
            self.browser.send_keys(Keys.ENTER, self)
        return changed


class Card(View):
    """Each card in host view has it's own title with same locator"""

    title = Text('.//div[@class="pf-c-card__title"]')


class DropdownWithDescripton(Dropdown):
    """Dropdown with description below items"""

    ITEM_LOCATOR = ".//*[contains(@class, 'pf-c-dropdown__menu-item') and contains(text(), {})]"


class HostDetailsCard(Widget):
    """Details card body contains multiple host detail information"""

    LABELS = '//div[@class="pf-c-description-list__group"]//dt//span'
    VALUES = '//div[@class="pf-c-description-list__group"]//dd//descendant::*/text()/..'

    def read(self):
        """Return a dictionary where keys are property names and values are property values.
        Values are either in span elements or in div elements
        """
        items = {}
        labels = self.browser.elements(f'{self.parent.ROOT}{self.LABELS}')
        values = self.browser.elements(f'{self.parent.ROOT}{self.VALUES}')
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
    breadcrumb = BreadCrumb('breadcrumbs-list')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Hosts'

    edit = OUIAButton('OUIA-Generated-Button-secondary-1')
    dropdown = Dropdown(locator='//button[@id="hostdetails-kebab"]/..')
    schedule_job = Pf4ActionsDropdown(locator='.//div[div/button[@aria-label="Select"]]')

    @View.nested
    class overview(Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class details(Card):
            ROOT = './/article[.//div[text()="Details"]]'
            details = HostDetailsCard()

        @View.nested
        class host_status(Card):
            ROOT = './/article[.//span[text()="Host status"]]'
            status = Text('.//h4[contains(@data-ouia-component-id, "global-state-title")]')

            status_success = Text('.//a[span[@class="status-success"]]')
            status_warning = Text('.//a[span[@class="status-warning"]]')
            status_error = Text('.//a[span[@class="status-error"]]')
            status_disabled = Text('.//a[span[@class="disabled"]]')

        class recent_audits(Card):
            ROOT = './/article[.//div[text()="Recent audits"]]'

            all_audits = Text('.//a[normalize-space(.)="All audits"]')
            table = SatTableWithoutHeaders(locator='.//table[@aria-label="audits table"]')

        @View.nested
        class installable_errata(Card):
            ROOT = './/article[.//div[text()="Installable errata"]]'

            security_advisory = Text('.//a[contains(@href, "type=security")]')
            bug_fixes = Text('.//a[contains(@href, "type=bugfix")]')
            enhancements = Text('.//a[contains(@href, "type=enhancement")]')

        @View.nested
        class total_risks(Card):
            ROOT = './/article[.//div[text()="Total risks"]]'

            low = Text('.//*[@id="legend-labels-0"]/*')
            moderate = Text('.//*[@id="legend-labels-1"]/*')
            important = Text('.//*[@id="legend-labels-2"]/*')
            critical = Text('.//*[@id="legend-labels-3"]/*')

        @View.nested
        class recent_jobs(Card):
            ROOT = './/article[.//div[text()="Recent jobs"]]'
            actions = Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]')

            class finished(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

            class running(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

            class scheduled(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

    @View.nested
    class content(Tab):
        # TODO Setting ROOT is just a workaround because of BZ 2119076,
        # once this gets fixed we should use the parametrized locator from Tab class
        ROOT = './/div'

        @View.nested
        class packages(Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="packages-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')
            status_filter = Dropdown(locator='.//div[@aria-label="select Status container"]/div')
            upgrade = Pf4ActionsDropdown(
                locator='.//div[div/button[normalize-space(.)="Upgrade"]]'
            )
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
        class errata(Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="errata-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')
            type_filter = Select(locator='.//div[@aria-label="select Type container"]/div')
            severity_filter = Select(locator='.//div[@aria-label="select Severity container"]/div')
            apply = Pf4ActionsDropdown(locator='.//div[@aria-label="errata_dropdown"]')
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
        class module_streams(Tab):
            TAB_NAME = 'Module streams'
            # workaround for BZ 2119076
            ROOT = './/div[@id="modulestreams-tab"]'

            searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')
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
                    5: DropdownWithDescripton(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                },
            )
            pagination = Pagination()

        @View.nested
        class repository_sets(Tab):
            TAB_NAME = 'Repository sets'
            # workaround for BZ 2119076
            ROOT = './/div[@id="repo-sets-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')
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
    class traces(Tab):
        enable_traces = OUIAButton('OUIA-Generated-Button-primary-1')

    @View.nested
    class insights(Tab):
        pass

    @View.nested
    class ansible(SatTab):
        """View comprising the subtabs under the Ansible Tab"""
        ROOT = './/div[contains(@class, "ansible-host-details")]'
        TAB_NAME = 'Ansible'

        @View.nested
        class roles(SatTab):
            TAB_NAME = 'Roles'
            assignedRoles = Text('.//a[contains(@href, "roles/all")]')
            edit = Button(locator='.//button[@aria-label="edit ansible roles"]')
            table = PatternflyTable(
                #No OUIA ID
                locator='',
                column_widgets={
                    'Name': Text('.//a')
                },
            )

        @View.nested
        class variables(SatTab):
            TAB_NAME = 'Variables'
            table = PatternflyTable(
                #No OUIA ID
                locator='',
                column_widgets={
                    'Name': Text('.//a'),
                    'Ansible role': Text('./span'),
                    'Type': Text('./span'),
                    #the next field can also be a form group
                    'Value': Text('./span'),
                    'Source attribute': Text('./span'),
                    #The next 2 buttons are hidden by default, but appear in this order
                    5: Button(locator='.//button[@aria-label="Cancel editing override button"]'),
                    6: Button(locator='.//button[@aria-label="Submit override button"]'),
                    #Clicking this button hides it, and displays the previous 2
                    7: Button(locator='.//button[@aria-label="Edit override button"]')
                },
            )

        @View.nested
        class inventory(SatTab):
            TAB_NAME = 'Inventory'
            ROOT = ""

        @View.nested
        class jobs(SatTab):
            TAB_NAME = 'Jobs'
            #Only displays when there isn't a Job scheduled for this host
            scheduleRecurringJob = Button(locator='.//button[@aria-label="schedule recurring job"]')

            #Mutually Exclusive with the above button
            scheduledJobsTable = PatternflyTable(
                #No OUIA ID
                locator='',
                column_widgets={
                    'Description': Text('.//a'),
                    'Schedule': Text('./span'),
                    'Next Run': Text('./span'),
                    4: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                }
            )

            #Only displayed on Refresh when there are previously executed jobs
            previousJobsTable = PatternflyTable(
                #No OUIA ID
                locator='',
                column_widgets={
                    'Description': Text('.//a'),
                    'Result': Text('./span'),
                    'State': Text('./span'),
                    'Executed at': Text('./span'),
                    'Schedule': Text('./span')
                }
            )


class InstallPackagesView(View):
    """Install packages modal"""

    ROOT = './/div[@id="package-install-modal"]'

    select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
    searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')

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


class EditAnsibleRolesView(View):
    """Edit Ansible Roles Modal"""

    ROOT = ''
    #No current representation for this Widget in Widgetastic


class ModuleStreamDialog(Pf4ConfirmationDialog):

    confirm_dialog = Button(locator='.//button[@aria-label="confirm-module-action"]')
    cancel_dialog = Button(locator='.//button[@aria-label="cancel-module-action"]')
    
class RecurringJobDialog(Pf4ConfirmationDialog):

    confirm_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-confirm"]')
    cancel_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-cancel"]')
