import time

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
from widgetastic_patternfly4.ouia import FormSelect as OUIAFormSelect
from widgetastic_patternfly4.ouia import PatternflyTable
from widgetastic_patternfly4.ouia import Select as OUIASelect

from airgun.views.common import BaseLoggedInView
from airgun.widgets import Accordion
from airgun.widgets import CheckboxGroup
from airgun.widgets import ItemsList
from airgun.widgets import Pf4ActionsDropdown
from airgun.widgets import Pf4ConfirmationDialog
from airgun.widgets import SatTableWithoutHeaders
from airgun.widgets import SearchInput


class RemediationView(View):
    """Remediation window view"""

    ROOT = './/div[@id="remediation-modal"]'
    remediate = Button("Remediate")
    cancel = Button("Cancel")
    table = PatternflyTable(
        component_id='OUIA-Generated-Table-4',
        column_widgets={
            'Hostname': Text('.//td[1]'),
            'Recommendation': Text('.//td[2]'),
            'Resolution': Text('.//td[3]'),
            'Reboot Required': Text('.//td[4]'),
        },
    )

    @property
    def is_displayed(self):
        return self.title.wait_displayed()


class Card(View):
    """Each card in host view has it's own title with same locator"""

    title = Text('.//div[@class="pf-c-card__title"]')


class DropdownWithDescripton(Dropdown):
    """Dropdown with description below items"""

    ITEM_LOCATOR = ".//*[contains(@class, 'pf-c-dropdown__menu-item') and contains(text(), {})]"


class HostDetailsCard(Widget):
    """Overview/Details & Details/SystemProperties card body contains multiple host detail info"""

    LABELS = '//div[@class="pf-c-description-list__group"]//dt//span'
    VALUES = '//div[@class="pf-c-description-list__group"]//*[self::dd or self::ul]'

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


class HostColectionsList(Widget):
    """Host collections list in host details page"""

    ROOT = './/div[@class="pf-c-card__body host-collection-card-body"]'
    ITEMS = './/span[contains(@class, "pf-c-expandable-section__toggle-text")]'

    def read(self):
        """Return a list of assigned host collections"""
        return [self.browser.text(item) for item in self.browser.elements(self.ITEMS)]


class NewHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb('breadcrumbs-list')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Hosts'

    edit = OUIAButton('host-edit-button')
    dropdown = Dropdown(locator='//button[@id="hostdetails-kebab"]/..')
    schedule_job = Pf4ActionsDropdown(locator='.//div[div/button[@aria-label="Select"]]')

    @View.nested
    class overview(Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class details(Card):
            ROOT = './/article[.//div[text()="Details"]]'

            details = HostDetailsCard()

            power_operations = OUIAButton('power-status-dropdown-toggle')

        @View.nested
        class host_status(Card):
            ROOT = './/article[.//span[text()="Host status"]]'

            status = Text('.//h4[contains(@data-ouia-component-id, "global-state-title")]')
            manage_all_statuses = Text('.//a[normalize-space(.)="Manage all statuses"]')

            status_success = Text('.//a[span[@class="status-success"]]')
            status_warning = Text('.//a[span[@class="status-warning"]]')
            status_error = Text('.//a[span[@class="status-error"]]')
            status_disabled = Text('.//a[span[@class="disabled"]]')

        class recent_audits(Card):
            ROOT = './/article[.//div[text()="Recent audits"]]'

            all_audits = Text('.//a[normalize-space(.)="All audits"]')
            table = SatTableWithoutHeaders(locator='.//table[@aria-label="audits table"]')

        @View.nested
        class recent_communication(Card):
            ROOT = './/article[.//div[text()="Recent communication"]]'

            last_checkin_value = Text('.//div[@class="pf-c-description-list__text"]')

        @View.nested
        class errata(Card):
            ROOT = './/article[.//div[text()="Errata"]]'

            enable_repository_sets = Text('.//a[normalize-space(.)="Enable repository sets"]')

        @View.nested
        class content_view_details(Card):
            ROOT = './/article[.//div[text()="Content view details"]]'
            actions = Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]')

            org_view = Text('.//a[contains(@href, "content_views")]')

        @View.nested
        class installable_errata(Card):
            ROOT = './/article[.//div[text()="Installable errata"]]'

            security_advisory = Text('.//a[contains(@href, "type=security")]')
            bug_fixes = Text('.//a[contains(@href, "type=bugfix")]')
            enhancements = Text('.//a[contains(@href, "type=enhancement")]')

        @View.nested
        class total_risks(Card):
            ROOT = './/article[.//div[text()="Total risks"]]'
            actions = Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]')

            low = Text('.//*[@id="legend-labels-0"]/*')
            moderate = Text('.//*[@id="legend-labels-1"]/*')
            important = Text('.//*[@id="legend-labels-2"]/*')
            critical = Text('.//*[@id="legend-labels-3"]/*')

        @View.nested
        class host_collections(Card):
            ROOT = './/article[.//div[text()="Host collections"]]'
            kebab_menu = Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]')
            no_host_collections = Text('.//h2')
            add_to_host_collection = OUIAButton('add-to-a-host-collection-button')

            assigned_host_collections = HostColectionsList()

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
        class system_purpose(Card):
            ROOT = './/article[.//div[text()="System purpose"]]'
            edit_system_purpose = Text(
                './/button[@data-ouia-component-id="syspurpose-edit-button"]'
            )

            role = Text('.//dd[contains(@class, "pf-c-description-list__description")][1]')
            sla = Text('.//dd[contains(@class, "pf-c-description-list__description")][2]')
            usage_type = Text('.//dd[contains(@class, "pf-c-description-list__description")][3]')
            release_version = Text(
                './/dd[contains(@class, "pf-c-description-list__description")][4]'
            )
            addons = Text('.//dd[contains(@class, "pf-c-description-list__description")][5]')

    @View.nested
    class details(Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        card_collapse_switch = Text(
            './/button[contains(@data-ouia-component-id, "expand-button")]'
        )

        @View.nested
        class system_properties(Card):
            ROOT = './/article[.//div[text()="System properties"]]'

            sys_properties = HostDetailsCard()

        @View.nested
        class operating_system(Card):
            ROOT = './/article[.//div[text()="Operating system"]]'

            architecture = Text(
                './/a[contains(@data-ouia-component-id, "OUIA-Generated-Button-link-1")]'
            )
            os = Text('.//a[contains(@data-ouia-component-id, "OUIA-Generated-Button-link-2")]')
            boot_time = Text('.//div[contains(@class, "pf-c-description-list__group")][3]/dd/div')
            kernel_release = Text(
                './/div[contains(@class, "pf-c-description-list__group")][4]/dd/div'
            )

        @View.nested
        class provisioning(Card):
            ROOT = './/article[.//div[text()="Provisioning"]]'

            build_duration = Text(
                './/div[contains(@class, "pf-c-description-list__group")][1]/dd/div'
            )
            token = Text('.//div[contains(@class, "pf-c-description-list__group")][2]/dd/div')
            pxe_loader = Text('.//div[contains(@class, "pf-c-description-list__group")][3]/dd/div')

        @View.nested
        class bios(Card):
            ROOT = './/article[.//div[text()="BIOS"]]'

            vendor = Text('.//div[contains(@class, "pf-c-description-list__group")][1]/dd/div')
            version = Text('.//div[contains(@class, "pf-c-description-list__group")][2]/dd/div')
            release_date = Text(
                './/div[contains(@class, "pf-c-description-list__group")][3]/dd/div'
            )

        @View.nested
        class registration_details(Card):
            ROOT = './/article[.//div[text()="Registration details"]]'

            registered_on = Text(
                './/div[contains(@class, "pf-c-description-list__group")][1]/dd/div'
            )
            registration_type = Text(
                './/div[contains(@class, "pf-c-description-list__group")][2]/ul/h4'
            )
            activation_key_name = Text(
                './/div[contains(@class, "pf-c-description-list__group")][2]//a'
            )
            registered_through = Text(
                './/div[contains(@class, "pf-c-description-list__group")][3]/dd/div'
            )

        @View.nested
        class hw_properties(Card):
            ROOT = './/article[.//div[text()="HW properties"]]'

            model = Text('.//div[contains(@class, "pf-c-description-list__group")][1]//dd')
            number_of_cpus = Text(
                './/div[contains(@class, "pf-c-description-list__group")][2]//dd'
            )
            sockets = Text('.//div[contains(@class, "pf-c-description-list__group")][3]//dd')
            cores_per_socket = Text(
                './/div[contains(@class, "pf-c-description-list__group")][4]//dd'
            )
            ram = Text('.//div[contains(@class, "pf-c-description-list__group")][5]//dd')
            storage = Text('.//div[contains(@class, "pf-c-description-list__group")][6]//h4')

        @View.nested
        class provisioning_templates(Card):
            ROOT = './/article[.//div[text()="Provisioning templates"]]'

            templates_table = SatTableWithoutHeaders(
                locator='.//table[@aria-label="templates table"]'
            )

        @View.nested
        class installed_products(Card):
            ROOT = './/article[.//div[text()="Installed products"]]'

            installed_products_list = ItemsList(locator='.//ul[contains(@class, "pf-c-list")]')

        @View.nested
        class networking_interfaces(Card):
            ROOT = './/article[.//div[text()="Networking interfaces"]]'

            networking_interfaces_accordion = Accordion(
                locator='.//div[contains(@class, "pf-c-card__expandable-content")]'
            )
            locator_templ = (
                './/div[contains(@class, "pf-c-accordion__expanded-content-body")]'
                '//div[.//dt[normalize-space(.)="{}"]]//div'
            )
            networking_interfaces_dict = {
                'fqdn': Text(locator_templ.format('FQDN')),
                'ipv4': Text(locator_templ.format('IPv4')),
                'ipv6': Text(locator_templ.format('IPv6')),
                'mac': Text(locator_templ.format('MAC')),
                'subnet': Text(locator_templ.format('Subnet')),
                'mtu': Text(locator_templ.format('MTU')),
            }
            edit_interfaces = Text('.//a[contains(@href, "/hosts/")]')

        @View.nested
        class networking_interface(Card):
            pass

        @View.nested
        class virtualization(Card):
            ROOT = './/article[contains(@data-ouia-component-id, "card-template-Virtualization")]'

            details = HostDetailsCard()

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
            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-c-text-input-group__text-input")]'
            )
            show_all = Button(locator='.//div[button[@aria-label="No limit"]]')
            limit_to_environemnt = Button(
                locator='.//div[button[@aria-label="Limit to environment"]]'
            )
            status_filter = Select(locator='.//div[@aria-label="select Status container"]/div')
            repository_type = Select(
                locator='.//div[@aria-label="select Repository type container"]/div'
            )
            dropdown = Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = Table(
                locator='.//table[@aria-label="Content View Table"]',
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Repository': Text('./span'),
                    'Product': Text('./a'),
                    'Repository path': Text('./span'),
                    'Status': Text('.//span[contains(@class, "pf-c-label__content")]'),
                    'Repository Type': Text('./span'),
                    6: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                },
            )
            pagination = Pagination()

    @View.nested
    class parameters(Tab):
        ROOT = './/div'

        add_parameter = Button(locator='.//button[text()="Add parameter"]')
        searchbar = SearchInput(
            locator='//input[contains(@class, "pf-c-search-input__text-input")]'
        )
        parameter_name_input = TextInput(locator='.//td//input[contains(@aria-label, "name")]')
        parameter_type_input = Select(
            locator='.//td[2]//div[@data-ouia-component-type="PF4/Select"]'
        )
        parameter_value_input = TextInput(locator='.//td[3]//textarea')
        cancel_addition = Button(locator='.//td[5]//button[1]')
        confirm_addition = Button(locator='.//td[5]//button[2]')

        table_header = PatternflyTable(locator='.//table[@data-ouia-component-type="PF4/Table"]')
        parameters_table = Table(
            locator='.//table[@aria-label="Parameters table"]',
            column_widgets={
                'Name': Text('.//td[contains(@data-label, "Name")]'),
                'Type': Text('.//td[contains(@data-label, "Type")]'),
                'Value': Text('.//td[contains(@data-label, "Value")]'),
                'Source': Text('.//td[contains(@data-label, "Source")]'),
                4: Button(
                    locator=(
                        './/button'
                        '[contains(@data-ouia-component-id, "OUIA-Generated-Button-plain-")]'
                    )
                ),
                5: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class traces(Tab):
        ROOT = './/div'

        title = Text('//h2')
        enable_traces = OUIAButton('enable-traces-button')
        select_all = Checkbox(locator='.//input[contains(@aria-label, "Select all")]')
        searchbar = SearchInput(locator='.//input[contains(@aria-label, "Select all")]')
        Pf4ActionsDropdown = Button(
            locator='.//div[contains(@aria-label, "bulk_actions_dropdown")]'
        )
        traces_table = PatternflyTable(
            component_id='host-traces-table',
            column_widgets={
                0: Checkbox(locator='.//input[contains(@aria-label, "Select row")]'),
                'Application': Text('.//td[2]'),
                'Type': Text('.//td[3]'),
                'Helper': Text('.//td[4]'),
                4: Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class ansible(Tab):
        """View comprising the subtabs under the Ansible Tab"""

        ROOT = './/div'

        @View.nested
        class roles(Tab):
            TAB_NAME = 'Roles'
            ROOT = './/div[@class="ansible-host-detail"]'

            assignedRoles = Text('.//a[contains(@href, "roles/all")]')
            edit = Button(locator='.//button[@aria-label="edit ansible roles"]')
            table = Table(
                locator='.//table[contains(@class, "pf-c-table")]',
                column_widgets={'Name': Text('.//a')},
            )
            pagination = Pagination()

        @View.nested
        class variables(Tab):
            TAB_NAME = 'Variables'
            ROOT = './/div[@class="ansible-host-detail"]'
            table = Table(
                locator='.//table[contains(@class, "pf-c-table")]',
                column_widgets={
                    'Name': Text('.//a'),
                    'Ansible role': Text('./span'),
                    'Type': Text('./span'),
                    # the next field can also be a form group
                    'Value': Text('./span'),
                    'Source attribute': Text('./span'),
                    # The next 2 buttons are hidden by default, but appear in this order
                    5: Button(locator='.//button[@aria-label="Cancel editing override button"]'),
                    6: Button(locator='.//button[@aria-label="Submit override button"]'),
                    # Clicking this button hides it, and displays the previous 2
                    7: Button(locator='.//button[@aria-label="Edit override button"]'),
                },
            )
            pagination = Pagination()

        @View.nested
        class inventory(Tab):
            TAB_NAME = 'Inventory'
            ROOT = './/div[@class="ansible-host-detail"]'

        @View.nested
        class jobs(Tab):
            TAB_NAME = 'Jobs'
            ROOT = './/div[@class="ansible-host-detail"]'

            @property
            def is_displayed(self):
                return (
                    self.schedule.is_displayed
                    or self.jobs.is_displayed
                    or self.previous.is_displayed
                )

            @View.nested
            class schedule(Tab):
                # Only displays when there isn't a Job scheduled for this host
                scheduleRecurringJob = Button(
                    locator='.//button[@aria-label="schedule recurring job"]'
                )

                @property
                def is_displayed(self):
                    return self.scheduleRecurringJob.is_displayed

            @View.nested
            class jobs(Tab):
                # Mutually Exclusive with the above button
                scheduledText = './/h3[text()="Scheduled recurring jobs"]'
                scheduledJobsTable = Table(
                    locator='.//div[contains(@class, "pf-c-table)"]',
                    column_widgets={
                        'Description': Text('.//a'),
                        'Schedule': Text('./span'),
                        'Next Run': Text('./span'),
                        4: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
                    },
                )
                pagination = Pagination()

                @property
                def is_displayed(self):
                    return self.scheduledText.is_displayed

            @View.nested
            class previous(Tab):
                # Only displayed on Refresh when there are previously executed jobs
                previousText = './/h3[text()="Previously executed jobs"]'
                previousJobsTable = Table(
                    locator='',
                    column_widgets={
                        'Description': Text('.//a'),
                        'Result': Text('./span'),
                        'State': Text('./span'),
                        'Executed at': Text('./span'),
                        'Schedule': Text('./span'),
                    },
                )
                pagination = Pagination()

                @property
                def is_displayed(self):
                    return self.previousText.is_displayed

    @View.nested
    class puppet(Tab):
        ROOT = './/div'

        search_bar = SearchInput(locator='.//input[contains(@class, "search-input")]')
        puppet_reports_table = PatternflyTable(
            component_id='reports-table',
            column_widgets={
                'reported_at': Text('.//a'),
                'failed': Text('.//td[2]'),
                'failed_restarts': Text('.//td[3]'),
                'restarted': Text('.//td[4]'),
                'applied': Text('.//td[5]'),
                'skipped': Text('.//td[6]'),
                'pending': Text('.//td[7]'),
                7: Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = Pagination()

        @View.nested
        class enc_preview(Tab):
            ROOT = './/div[@class="enc-preview-tab"]'
            TAB_NAME = "ENC Preview"
            preview = Text('.//code')

        @View.nested
        class puppet_details(Card):
            ROOT = './/article[.//div[text()="Puppet details"]]'
            puppet_environment = Text(
                './div[2]//div[contains(@class, "pf-c-description-list__group")][1]//dd'
            )
            puppet_capsule = Text(
                './div[2]//div[contains(@class, "pf-c-description-list__group")][2]//dd'
            )
            puppet_ca_capsule = Text(
                './div[2]//div[contains(@class, "pf-c-description-list__group")][3]//dd'
            )

    @View.nested
    class reports(Tab):
        ROOT = './/div'

        search_bar = SearchInput(locator='.//input[contains(@class, "search-input")]')
        reports_table = PatternflyTable(
            component_id='reports-table',
            column_widgets={
                'reported_at': Text('.//a'),
                'failed': Text('.//td[2]'),
                'failed_restarts': Text('.//td[3]'),
                'restarted': Text('.//td[4]'),
                'applied': Text('.//td[5]'),
                'skipped': Text('.//td[6]'),
                'origin': Text('.//td[7]'),
                'pending': Text('.//td[8]'),
                8: Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )

        pagination = Pagination()

    @View.nested
    class insights(Tab):
        ROOT = './/div'

        search_bar = SearchInput(locator='.//input[contains(@class, "search-input")]')
        remediate = Button(locator='.//button[text()="Remediate"]')
        insights_dropdown = Dropdown(locator='.//div[contains(@class, "insights-dropdown")]')

        select_all_one_page = Checkbox(locator='.//input[@name="check-all"]')
        select_all_pages = Button(
            locator='.//button[text()="Select recommendations from all pages"]'
        )

        recommendations_table = PatternflyTable(
            component_id='OUIA-Generated-Table-2',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Recommendation': Text('.//td[2]'),
                'Total Risk': Text('.//td[3]'),
                'Remediate': Text('.//td[4]'),
                4: Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = Pagination()


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


class AllAssignedRolesView(View):
    """All Assigned Roles Modal"""

    ROOT = './/div[@data-ouia-component-id="modal-ansible-roles"]'

    table = Table(
        locator='.//table[contains(@class, "pf-c-table")]',
        column_widgets={'Name': Text('.//a'), 'Source': Text('.//a')},
    )
    pagination = Pagination()


class EnableTracerView(View):
    """Enable Tracer Modal"""

    ROOT = './/div[@data-ouia-component-id="enable-tracer-modal"]'

    confirm = Button(locator='//*[@data-ouia-component-id="enable-tracer-modal"]/footer/button[1]')


class ParameterDeleteDialog(View):
    """Confirmation dialog for deleting host parameter"""

    ROOT = './/div[@data-ouia-component-id="app-confirm-modal"]'

    confirm_delete = OUIAButton('btn-modal-confirm')
    cancel_delete = OUIAButton('btn-modal-cancel')


class ManageHostCollectionModal(View):
    """Host Collection Modal"""

    ROOT = './/div[@data-ouia-component-id="host-collections-modal"]'

    create_host_collection = OUIAButton('empty-state-primary-action-button')
    select_all = Checkbox(locator='.//input[contains(@aria-label, "Select all")]')
    searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')

    host_collection_table = Table(
        locator='.//table[contains(@class, "pf-c-table")]',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'host_collecntion': Text('.//a'),
            'capacity': Text('.//td[3]'),
            'description': Text('.//td[4]'),
        },
    )

    pagination = Pagination()

    add = OUIAButton('add-button')
    remove = OUIAButton('add-button')
    cancel = OUIAButton('cancel-button')


class EditSystemPurposeView(View):
    """Edit System Purpose Modal"""

    ROOT = './/div[@data-ouia-component-id="syspurpose-edit-modal"]'

    role = OUIAFormSelect('role-select')
    sla = OUIAFormSelect('service-level-select')
    usage = OUIAFormSelect('usage-select')
    release_version = OUIAFormSelect('release-version-select')
    add_ons = OUIASelect('syspurpose-addons-select')

    save = OUIAButton('save-syspurpose')
    cancel = OUIAButton('cancel-syspurpose')


class EditAnsibleRolesView(View):
    """Edit Ansible Roles Modal"""

    ROOT = ''
    # No current representation for this Widget in Widgetastic


class ModuleStreamDialog(Pf4ConfirmationDialog):

    confirm_dialog = Button(locator='.//button[@aria-label="confirm-module-action"]')
    cancel_dialog = Button(locator='.//button[@aria-label="cancel-module-action"]')


class RecurringJobDialog(Pf4ConfirmationDialog):

    confirm_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-confirm"]')
    cancel_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-cancel"]')


class PF4CheckboxTreeView(CheckboxGroup):
    """
    Modified :class:`airgun.widgets.CheckboxGroup` for PF4 tree view with checkboxes:
        https://www.patternfly.org/v4/components/tree-view#with-checkboxes
    """

    ITEMS_LOCATOR = './/*[self::span|self::label][contains(@class, "pf-c-tree-view__node-text")]'
    CHECKBOX_LOCATOR = (
        './/*[self::span|self::label][contains(@class, "pf-c-tree-view__node-text")]'
        '[normalize-space(.)="{}"]/preceding-sibling::span/input[@type="checkbox"]'
    )


class ManageColumnsView(BaseLoggedInView):
    """Manage columns modal."""

    ROOT = '//div[contains(@class, "pf-c-modal-box")]'

    CHECKBOX_SECTION_TOGGLE = (
        './/*[self::span|self::label][contains(@class, "pf-c-tree-view__node-text")]'
        '[normalize-space(.)="{}"]/preceding-sibling::button'
    )
    DEFAULT_COLLAPSED_SECTIONS = [
        CHECKBOX_SECTION_TOGGLE.format('Content'),
        CHECKBOX_SECTION_TOGGLE.format('Network'),
        CHECKBOX_SECTION_TOGGLE.format('Reported data'),
        CHECKBOX_SECTION_TOGGLE.format('RH Cloud'),
    ]
    is_tree_collapsed = True
    title = Text(
        './/header//span[contains(@class, "pf-c-modal-box__title")]'
        '[normalize-space(.)="Manage columns"]'
    )
    confirm_dialog = Button(locator='.//button[normalize-space(.)="Save"]')
    cancel_dialog = Button(locator='.//button[normalize-space(.)="Cancel"]')
    checkbox_group = PF4CheckboxTreeView(locator='.//div[contains(@class, "pf-c-tree-view")]')

    def collapsed_sections(self):
        return (self.browser.element(locator) for locator in self.DEFAULT_COLLAPSED_SECTIONS)

    @property
    def is_displayed(self):
        title = self.browser.wait_for_element(self.title, exception=False)
        return title is not None and title.is_diaplyed()

    def expand_all(self):
        """Expand all tree sections that are collapsed by default"""
        if self.is_tree_collapsed:
            for checkbox_group in self.collapsed_sections():
                checkbox_group.click()
                self.is_tree_collapsed = False

    def read(self):
        """
        Get labels and values of all checkboxes in the dialog.

        :return dict: mapping of `label: value` items
        """
        self.expand_all()
        return self.checkbox_group.read()

    def fill(self, values):
        """
        Set value of given checkboxes.
        Example: values={'Operating system': True, 'Owner': False}

        :param dict values: mapping of `label: value` items
        """
        self.expand_all()
        self.checkbox_group.fill(values)

    def submit(self):
        """Submit the dialog and wait for the page to reload."""
        self.confirm_dialog.click()
        # the submit and page reload does not kick in immediately
        # so ensure_page_safe() does not catches it
        time.sleep(2)
        self.browser.plugin.ensure_page_safe()
