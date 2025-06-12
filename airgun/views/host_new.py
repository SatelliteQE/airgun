import time

from widgetastic.widget import Checkbox, Text, TextInput, View, Widget
from widgetastic.widget.table import Table
from widgetastic_patternfly4 import (
    Button,
    Dropdown,
    DualListSelector,
    Pagination as PF4Pagination,
    Select,
    Tab,
)
from widgetastic_patternfly4.ouia import (
    BreadCrumb,
    Button as OUIAButton,
    ExpandableTable,
    FormSelect as OUIAFormSelect,
    PatternflyTable,
)
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Dropdown as PF5Dropdown,
    Menu as PF5Menu,
    Pagination as PF5Pagination,
    Tab as PF5Tab,
)
from widgetastic_patternfly5.ouia import (
    Button as PF5OUIAButton,
    PatternflyTable as PF5OUIATable,
)

from airgun.views.common import BaseLoggedInView
from airgun.widgets import (
    Accordion,
    ActionsDropdown,
    CheckboxGroup,
    ItemsList,
    Pf4ActionsDropdown,
    Pf4ConfirmationDialog,
    SatTableWithoutHeaders,
    SearchInput,
)


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
            _value = self.browser.text(value)
            _key = self.browser.text(key).replace(' ', '_').lower()
            items[_key] = _value
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
    dropdown = PF5Dropdown(locator='//button[@id="hostdetails-kebab"]/..')
    schedule_job = Pf4ActionsDropdown(locator='.//div[div/button[@aria-label="Select"]]')
    run_job = ActionsDropdown('//button[@data-ouia-component-id="schedule-a-job-dropdown-toggle"]')
    select = Text(
        '//ul[@class="pf-c-dropdown__menu pf-m-align-right"]/li/a/div[normalize-space(text())="Run Ansible roles"]'
    )

    @View.nested
    class overview(PF5Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class details(Card):
            ROOT = './/article[.//div[text()="Details"]]'
            edit = Text('.//div[@class="pf-c-description-list__group"]/dd//div[2]')
            details = HostDetailsCard()

            power_operations = OUIAButton('power-status-dropdown-toggle')

        @View.nested
        class host_status(Card):
            ROOT = './/div[@data-ouia-component-id="card-aggregate-status"]'

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

            details = HostDetailsCard()

    @View.nested
    class details(PF5Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        card_collapse_switch = Text('.//button[contains(@data-ouia-component-id, "expand-button")]')

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

            details = HostDetailsCard()

        @View.nested
        class provisioning(Card):
            ROOT = './/article[.//div[text()="Provisioning"]]'

            details = HostDetailsCard()

        @View.nested
        class bios(Card):
            ROOT = './/article[.//div[text()="BIOS"]]'

            details = HostDetailsCard()

        @View.nested
        class registration_details(Card):
            ROOT = './/article[.//div[text()="Registration details"]]'

            details = HostDetailsCard()

        @View.nested
        class hw_properties(Card):
            ROOT = './/article[.//div[text()="HW properties"]]'

            details = HostDetailsCard()

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
        class bootc(Card):
            # Will file issue for this to be fixed
            ROOT = './/article[contains(@data-ouia-component-id, "card-template-image-mode")]'

            remote_execution_link = Text(".//a[normalize-space(.)='Modify via remote execution']")
            details = HostDetailsCard()

    @View.nested
    class content(PF5Tab):
        # TODO Setting ROOT is just a workaround because of BZ 2119076,
        # once this gets fixed we should use the parametrized locator from Tab class
        ROOT = './/div'

        @View.nested
        class packages(PF5Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="packages-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-c-text-input-group__text-input")]'
            )
            status_filter = Dropdown(locator='.//div[@aria-label="select Status container"]/div')
            upgrade = Pf4ActionsDropdown(locator='.//div[div/button[normalize-space(.)="Upgrade"]]')
            dropdown = PF5Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

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
            pagination = PF4Pagination()

        @View.nested
        class errata(PF5Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="errata-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(locator='.//input[contains(@class, "pf-c-text-input")]')
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
            pagination = PF4Pagination(
                "//div[@class = 'pf-c-pagination pf-m-bottom tfm-pagination']"
            )

        @View.nested
        class module_streams(PF5Tab):
            TAB_NAME = 'Module streams'
            # workaround for BZ 2119076
            ROOT = './/div[@id="modulestreams-tab"]'

            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-v5-c-text-input-group__text-input")]'
            )
            status_filter = Select(locator='.//div[@aria-label="select Status container"]/div')
            installation_status_filter = Select(
                locator='.//div[@aria-label="select Installation status container"]/div'
            )
            dropdown = PF5Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

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
            pagination = PF4Pagination()

        @View.nested
        class repository_sets(PF5Tab):
            TAB_NAME = 'Repository sets'
            # workaround for BZ 2119076
            ROOT = './/div[@id="repo-sets-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-v5-c-text-input-group__text")]'
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

            table = PF5OUIATable(
                component_id='host-repository-sets-table',
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Repository': Text('./span'),
                    'Product': Text('./a'),
                    'Repository path': Text('./span'),
                    'Status': Text('.//span[contains(@class, "pf-c-label__content")]'),
                    'Repository Type': Text('./span'),
                    6: PF5Button(locator='./button'),
                },
            )
            repo_set_action = PF5Menu(
                locator='.//td[contains(@class, "pf-v5-c-table__action")]/div[contains(@class, "pf-v5-c-menu")]/div'
            )
            pagination = PF4Pagination()

    @View.nested
    class parameters(PF5Tab):
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
        pagination = PF4Pagination()

    @View.nested
    class traces(PF5Tab):
        ROOT = './/div'

        title = Text('//h2')
        enable_traces = PF5OUIAButton('enable-traces-button')
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
        pagination = PF4Pagination()

    @View.nested
    class ansible(PF5Tab):
        """View comprising the subtabs under the Ansible Tab"""

        ROOT = './/div'

        @View.nested
        class roles(PF5Tab):
            TAB_NAME = 'Roles'
            ROOT = './/div[@class="ansible-host-detail"]'

            assignedRoles = Text('.//a[contains(@href, "roles/all")]')
            edit = Button(locator='.//button[@aria-label="edit ansible roles"]')
            noRoleAssign = Text('.//h5[contains(@class, "pf-c-title pf-m-4xl")]')
            table = Table(
                locator='.//table[contains(@class, "pf-c-table")]',
                column_widgets={'Name': Text('.//a')},
            )
            pagination = PF4Pagination()

        @View.nested
        class variables(PF5Tab):
            TAB_NAME = 'Variables'
            ROOT = './/div[@class="ansible-host-detail"]'

            actions = Button(locator='//tbody/tr/td[7]//button')
            delete = Button(locator='//button[@role="menuitem"]')
            confirm = Button(locator='//button[@data-ouia-component-id="btn-modal-confirm"]')
            table = Table(
                locator='.//table[contains(@class, "pf-c-table")]',
                column_widgets={
                    'Name': Text('.//a'),
                    'Ansible role': Text('./span'),
                    'Type': Text('./span'),
                    # the next field can also be a form group
                    'Value': TextInput(locator='//textarea[contains(@class, "pf-c-form")]'),
                    'Source attribute': Text('./span'),
                    # The next 2 buttons are hidden by default, but appear in this order
                    6: Button(locator='.//button[@aria-label="Cancel editing override button"]'),
                    7: Button(locator='.//button[@aria-label="Submit override button"]'),
                    # Clicking this button hides it, and displays the previous 2
                    5: Button(locator='.//button[@aria-label="Edit override button"]'),
                },
            )
            table1 = Table(
                locator='.//table[contains(@class, "pf-c-table")]',
                column_widgets={
                    5: Button(locator='.//button[@aria-label="Submit editing override button"]'),
                },
            )
            pagination = PF4Pagination()

        @View.nested
        class inventory(PF5Tab):
            TAB_NAME = 'Inventory'
            ROOT = './/div[@class="ansible-host-detail"]'

        @View.nested
        class jobs(PF5Tab):
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
            class schedule(PF5Tab):
                # Only displays when there isn't a Job scheduled for this host
                scheduleRecurringJob = Button(
                    locator='.//button[@aria-label="schedule recurring job"]'
                )

                @property
                def is_displayed(self):
                    return self.scheduleRecurringJob.is_displayed

            @View.nested
            class jobs(PF5Tab):
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
                pagination = PF4Pagination()

                @property
                def is_displayed(self):
                    return self.scheduledText.is_displayed

            @View.nested
            class previous(PF5Tab):
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
                pagination = PF4Pagination()

                @property
                def is_displayed(self):
                    return self.previousText.is_displayed

    @View.nested
    class puppet(PF5Tab):
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
        pagination = PF4Pagination()

        @View.nested
        class enc_preview(PF5Tab):
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
    class reports(PF5Tab):
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

        pagination = PF4Pagination()

    @View.nested
    class insights(PF5Tab):
        ROOT = './/div'

        search_bar = SearchInput(locator='.//input[contains(@class, "pf-v5-c-text-input")]')
        remediate = Button(locator='.//button[text()="Remediate"]')
        insights_dropdown = Dropdown(locator='.//div[contains(@class, "insights-dropdown")]')

        select_all_one_page = Checkbox(locator='.//input[@name="check-all"]')
        select_all_pages = Button(
            locator='.//button[text()="Select recommendations from all pages"]'
        )

        recommendations_table = PF5OUIATable(
            component_id='OUIA-Generated-Table-2',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Recommendation': Text('.//td[2]'),
                'Total Risk': Text('.//td[3]'),
                'Remediate': Text('.//td[4]'),
                4: Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = PF5Pagination()


class InstallPackagesView(View):
    """Install packages modal"""

    ROOT = './/div[@id="package-install-modal"]'

    select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
    searchbar = SearchInput(
        locator='.//input[contains(@class, "pf-v5-c-text-input-group__text-input")]'
    )

    table = Table(
        locator='.//table[@aria-label="Content View Table"]',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Package': Text('./parent::td'),
            'Version': Text('./parent::td'),
        },
    )
    pagination = PF4Pagination()

    install = Button(locator='.//button[(normalize-space(.)="Install")]')
    cancel = Button('Cancel')


class AllAssignedRolesView(View):
    """All Assigned Roles Modal"""

    ROOT = './/div[@data-ouia-component-id="modal-ansible-roles"]'

    table = Table(
        locator='.//table[contains(@class, "pf-c-table")]',
        column_widgets={'Name': Text('.//a'), 'Source': Text('.//a')},
    )
    pagination = PF4Pagination()


class EnableTracerView(View):
    """Enable Tracer Modal"""

    ROOT = './/div[@data-ouia-component-id="enable-tracer-modal"]'

    confirm = PF5OUIAButton('enable-button-via-rex')


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

    pagination = PF4Pagination()

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

    save = OUIAButton('save-syspurpose')
    cancel = OUIAButton('cancel-syspurpose')


class ManageHostStatusesView(View):
    """Manage host statuses modal"""

    ROOT = './/div[@data-ouia-component-id="statuses-modal"]'
    close_modal = Button(locator='.//button[@aria-label="Close"]')
    host_statuses_table = PF5OUIATable(
        component_id='statuses-table',
        column_widgets={
            'Name': Text('.//td[contains(@data-label, "Name")]'),
            'Status': Text('.//td[contains(@data-label, "Status")]'),
            'Reported at': Text('.//td[contains(@data-label, "Reported at")]'),
            3: Button(locator='.//td[contains(@class, "action")]'),
        },
    )

    def read(self):
        # Parses into a dictionary of {name: {status, reported_at}}
        return {value.pop('Name'): value for value in self.host_statuses_table.read()}


class EditAnsibleRolesView(View):
    """Edit Ansible Roles Modal"""

    addAnsibleRole = DualListSelector('//div[@class = "pf-c-dual-list-selector"]')
    confirm = Button(locator='.//button[@aria-label="submit ansible roles"]')
    hostAssignedAnsibleRoles = Text(
        './/button[@class="pf-c-dual-list-selector__item"]/span[1]//span[2]'
    )
    selectRoles = Button(locator='.//button[@aria-label="Add selected"]')
    unselectRoles = Button(locator='.//button[@aria-label="Remove selected"]')


class ModuleStreamDialog(Pf4ConfirmationDialog):
    confirm_dialog = Button(locator='.//button[@aria-label="confirm-module-action"]')
    cancel_dialog = Button(locator='.//button[@aria-label="cancel-module-action"]')


class RecurringJobDialog(Pf4ConfirmationDialog):
    confirm_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-confirm"]')
    cancel_dialog = Button(locator='.//button[@data-ouia-component-id="btn-modal-cancel"]')


class PF5CheckboxTreeView(CheckboxGroup):
    """
    Modified :class:`airgun.widgets.CheckboxGroup` for PF5 tree view with checkboxes:
       https://v5-archive.patternfly.org/components/tree-view#with-checkboxes
    """

    ITEMS_LOCATOR = './/*[self::span|self::label][contains(@class, "pf-v5-c-tree-view__node-text")]'
    CHECKBOX_LOCATOR = (
        './/*[self::span|self::label][contains(@class, "pf-v5-c-tree-view__node-text")]'
        '[normalize-space(.)="{}"]/preceding-sibling::span/input[@type="checkbox"]'
    )


class ManageColumnsView(BaseLoggedInView):
    """Manage columns modal."""

    ROOT = '//div[contains(@class, "pf-v5-c-modal-box")]'

    CHECKBOX_SECTION_TOGGLE = (
        './/*[self::span|self::label][contains(@class, "pf-v5-c-tree-view__node-text")]'
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
        './/header//span[contains(@class, "pf-v5-c-modal-box__title")]'
        '[normalize-space(.)="Manage columns"]'
    )
    confirm_dialog = Button(locator='.//button[normalize-space(.)="Save"]')
    cancel_dialog = Button(locator='.//button[normalize-space(.)="Cancel"]')
    checkbox_group = PF5CheckboxTreeView(locator='.//div[contains(@class, "pf-v5-c-tree-view")]')

    def collapsed_sections(self):
        return (self.browser.element(locator) for locator in self.DEFAULT_COLLAPSED_SECTIONS)

    @property
    def is_displayed(self):
        title = self.browser.wait_for_element(self.title, exception=False)
        return title is not None and title.is_displayed()

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
