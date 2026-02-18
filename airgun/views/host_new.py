import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import (
    Checkbox,
    ParametrizedView,
    Text,
    TextInput,
    View,
    Widget,
)
from widgetastic.widget.table import Table
from widgetastic.xpath import quote
from widgetastic_patternfly4 import (
    Button,
    Dropdown,
    DualListSelector,
    Pagination as PF4Pagination,
    Select,
    Tab,
)
from widgetastic_patternfly4.ouia import (
    Button as OUIAButton,
    FormSelect as OUIAFormSelect,
    PatternflyTable,
)
from widgetastic_patternfly5 import (
    Button as PF5Button,
    CompactPagination as PF5Pagination,
    Dropdown as PF5Dropdown,
    ExpandableTable as PF5ExpandableTable,
    Menu as PF5Menu,
    Modal as PF5Modal,
    Tab as PF5Tab,
)
from widgetastic_patternfly5.ouia import (
    Alert as PF5OUIAAlert,
    BreadCrumb,
    Button as PF5OUIAButton,
    Dropdown as PF5OUIADropdown,
    ExpandableTable as PF5OUIAExpandableTable,
    PatternflyTable as PF5OUIATable,
    Select as PF5OUIASelect,
    Switch as PF5OUIASwitch,
    Text as PF5OUIAText,
)

# from airgun.views.all_hosts import ManageCVEModal as ManageCVEnvModal
from airgun.views.cloud_insights import BulkSelectMenuToggle
from airgun.views.common import BaseLoggedInView, PF5LCESelectorGroup, SearchableViewMixinPF4
from airgun.widgets import (
    Accordion,
    ActionsDropdown,
    CheckboxGroup,
    ItemsList,
    Pf4ActionsDropdown,
    Pf5ConfirmationDialog,
    PF5LCESelector,
    SatTableWithoutHeaders,
    SearchInput,
)


class MenuToggleButtonMenu(PF5Dropdown):
    """
    This class is implementation of PF5 Dropdown/MenuToggle which is implemented like Button->Dropdown
    kebab menus in host -> Content -> Packages / Errata / Module streams tables.

    Note: Some table row kebab menu is implemented as a simple Dropdown widget (e.g., host Module streams)
    and some as a MenuToggle & Dropdown combo (e.g., host Packages, Errata).
    """

    ROOT = f'{PF5Dropdown.BUTTON_LOCATOR}/..'
    DEFAULT_LOCATOR = (
        f'{PF5Dropdown.BUTTON_LOCATOR}'
        '[@aria-label="Kebab toggle" or contains(@aria-label, "kebab-dropdown")'
    )


class RemediationView(View):
    """Remediation window view"""

    ROOT = './/div[@id="remediation-modal"]'
    remediate = Button('Remediate')
    cancel = Button('Cancel')
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
        return self.title.is_displayed


class Card(View):
    """Each card in host view has it's own title with same locator"""

    title = Text('.//div[@class="pf-v5-c-card__title"]')


class ContentViewDetailsCard(Card):
    """Reusable content view details card with LCE and CV information"""

    ROOT = './/div[@data-ouia-component-id="content-view-details-card"]'
    ITEMS = './/div[@class="pf-v5-l-flex pf-m-row pf-m-row-on-sm pf-m-wrap"]'
    LCE_NAME = './/span[@class="pf-v5-c-label__text"]'
    # CV can be either a link (custom CV) or plain text span (Default Organization View)
    CV_NAME = './/a[contains(@href, "content_views") and not(contains(@href, "versions"))] | .//div[@aria-label="content_view_icon"]/following-sibling::span[1]'
    CV_VERSION = './/a[contains(@href, "versions")]//span'

    dropdown = PF5Dropdown(locator='.//div[button[@aria-label="change_content_view_kebab"]]')

    org_view = Text('.//a[contains(@href, "content_views")]')

    def read(self):
        """Return a list of dictionaries containing LCE name, CV name, and CV version.

        Note: For long CV names, the UI truncates them with "..." so we strip that suffix.
        """
        items = []
        for item in self.browser.elements(self.ITEMS):
            lce_element = self.browser.element(self.LCE_NAME, parent=item)
            cv_element = self.browser.element(self.CV_NAME, parent=item)

            cv_text = self.browser.text(cv_element)
            # Strip "..." suffix if present (indicates truncation)
            if cv_text.endswith('...'):
                cv_text = cv_text[:-3]

            # Version is only present for custom content views, not for Default Organization View
            version_text = None
            try:
                cv_version_element = self.browser.element(self.CV_VERSION, parent=item)
                version_text = self.browser.text(cv_version_element)
            except NoSuchElementException:
                pass

            items.append(
                {
                    'lce': self.browser.text(lce_element),
                    'content_view': cv_text,
                    'version': version_text,
                }
            )
        return items


class DropdownWithDescription(PF5Dropdown):
    """Dropdown with description below items"""

    ITEM_LOCATOR = ".//*[contains(@class, 'pf-v5-c-dropdown__menu-item') and contains(text(), {})]"


class CVESelect(Select):
    BUTTON_LOCATOR = './/button[@aria-label="Options menu"]'
    # The dropdown menu is rendered with position:absolute outside the select widget
    # so we need to search from document root (//...) not relative (.//...)
    ITEMS_LOCATOR = '//ul[contains(@class, "pf-v5-c-select__menu")]/li'
    ITEM_LOCATOR = '//button[contains(@class, "pf-v5-c-select__menu-item") and contains(normalize-space(.), {})]'
    SELECTED_ITEM_LOCATOR = './/span[contains(@class, "ins-c-conditional-filter")]'
    TEXT_LOCATOR = './/div[contains(@class, "pf-v5-c-select") and child::button]'
    DEFAULT_LOCATOR = './/div[contains(@class, "pf-v5-c-select") and @data-ouia-component-id="select-content-view"]'
    SEARCH_INPUT_LOCATOR = (
        './/input[@type="text" and contains(@class, "pf-v5-c-select__toggle-typeahead")]'
    )

    # Maximum length before CV names are truncated in the UI
    CV_NAME_TRUNCATE_LENGTH = 45

    def item_select(self, item, **kwargs):
        """Override item_select to handle CV names with 'Version X.Y' suffix and truncation.

        The dropdown shows:
        - Short names: 'CV_NAME Version 1.0'  -> we search for 'CV_NAME' which is contained
        - Long names: 'CV_NAMETRUNC... Version 1.0' -> we search for first 45 chars which is contained

        For long names, the full CV name (e.g. 150 chars) is NOT contained in the truncated
        display (e.g. 47 chars + "..."), so we search by prefix instead.
        """
        self.open()
        time.sleep(1)  # Wait for dropdown to fully render

        # For long CV names, search by truncated prefix (first 45 chars)
        # For short CV names, the full name will be contained in "NAME Version 1.0"
        search_text = (
            item[: self.CV_NAME_TRUNCATE_LENGTH]
            if len(item) > self.CV_NAME_TRUNCATE_LENGTH
            else item
        )

        # Find button with contains() matching on the search text
        locator = f'//button[contains(@class, "pf-v5-c-select__menu-item") and contains(normalize-space(.), {quote(search_text)})]'

        try:
            elem = self.browser.element(locator)
            self.browser.click(elem)
            time.sleep(0.5)
        except NoSuchElementException:
            # If prefix match fails, try parent's method
            self.close()
            return super().item_select(item, **kwargs)


class HostDetailsCard(Widget):
    """Overview/Details & Details/SystemProperties card body contains multiple host detail info"""

    LABELS = '//div[@class="pf-v5-c-description-list__group"]//dt//span'
    VALUES = '//div[@class="pf-v5-c-description-list__group"]//*[self::dd or self::ul]'

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

    ROOT = './/div[@class="pf-v5-c-card__body host-collection-card-body"]'
    ITEMS = './/span[contains(@class, "pf-v5-c-expandable-section__toggle-text")]'

    def read(self):
        """Return a list of assigned host collections"""
        return [self.browser.text(item) for item in self.browser.elements(self.ITEMS)]


class HostsView(BaseLoggedInView, SearchableViewMixinPF4):
    """New All Hosts view.
    Note: This is a minimal implementation of the new Hosts page, and currently it serves only to transition
    to the now-legacy UI page.
    """

    title = Text('//h1[normalize-space(.)="Hosts"]')
    actions = PF5OUIADropdown(component_id='legacy-ui-kebab')
    table = PF5OUIATable(
        component_id='hosts-index-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text(
                './/a[contains(@href, "/new/hosts/") and not(contains(@href, "Red Hat Lightspeed"))]'
            ),
            'Recommendations': Text('./a'),
            6: MenuToggleButtonMenu(),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class NewHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb('breadcrumbs-list')

    @property
    def is_displayed(self):
        return self.breadcrumb.is_displayed and self.breadcrumb.locations[0] == 'Hosts'

    edit = PF5OUIAButton('host-edit-button')
    dropdown = PF5Dropdown(locator='//button[@id="hostdetails-kebab"]/..')
    schedule_job = Pf4ActionsDropdown(locator='.//div[div/button[@aria-label="Select"]]')
    run_job = ActionsDropdown('//button[@data-ouia-component-id="schedule-a-job-dropdown-toggle"]')
    select = Text(
        '//ul[@class="pf-v5-c-dropdown__menu pf-m-align-right"]/li/a/div[normalize-space(text())="Run Ansible roles"]'
    )

    @View.nested
    class overview(PF5Tab):
        ROOT = './/div[contains(@class, "host-details-tab-item")]'

        @View.nested
        class details(Card):
            ROOT = './/div[@data-ouia-component-id="details-card"]'
            edit = Text('.//div[@class="pf-v5-c-description-list__group"]/dd//div[2]')
            details = HostDetailsCard()
            power_operations = PF5OUIAButton('power-status-dropdown-toggle')

        @View.nested
        class host_status(Card):
            ROOT = './/div[@data-ouia-component-id="card-aggregate-status"]'

            status = Text('.//div[contains(@class, "pf-v5-c-empty-state__title")]')
            manage_all_statuses = Text('.//a[normalize-space(.)="Manage all statuses"]')

            status_success = Text('.//a[.//span[@class="status-success"]]')
            status_warning = Text('.//a[.//span[@class="status-warning"]]')
            status_error = Text('.//a[.//span[@class="status-error"]]')
            status_disabled = Text('.//a[.//span[@class="disabled"]]')

        class recent_audits(Card):
            ROOT = './/div[@data-ouia-component-id="audit-card"]'

            all_audits = Text('.//a[normalize-space(.)="All audits"]')
            table = SatTableWithoutHeaders(locator='.//table[@aria-label="audits table"]')

        @View.nested
        class recent_communication(Card):
            ROOT = './/div[@data-ouia-component-id="card-template-Recent communication"]'

            last_checkin_value = Text('.//div[@class="pf-v5-c-description-list__text"]')

        @View.nested
        class errata(Card):
            ROOT = './/article[.//div[text()="Errata"]]'

            enable_repository_sets = Text('.//a[normalize-space(.)="Enable repository sets"]')

        # Reuse the standalone ContentViewDetailsCard class
        content_view_details = ContentViewDetailsCard

        @View.nested
        class installable_errata(Card):
            ROOT = './/div[@data-ouia-component-id="errata-card"]'

            security_advisory = Text('.//a[contains(@href, "type=security")]')
            bug_fixes = Text('.//a[contains(@href, "type=bugfix")]')
            enhancements = Text('.//a[contains(@href, "type=enhancement")]')

        @View.nested
        class total_risks(Card):
            ROOT = './/div[@data-ouia-component-id="card-template-Total risks"]'
            actions = Dropdown(locator='.//div[contains(@class, "pf-v5-c-dropdown")]')

            low = Text('.//*[@id="legend-labels-0"]/*')
            moderate = Text('.//*[@id="legend-labels-1"]/*')
            important = Text('.//*[@id="legend-labels-2"]/*')
            critical = Text('.//*[@id="legend-labels-3"]/*')

        @View.nested
        class host_collections(Card):
            ROOT = './/div[@data-ouia-component-id="host-collections-card"]'
            kebab_menu = Dropdown(locator='.//div[contains(@class, "pf-v5-c-dropdown")]')
            no_host_collections = Text('.//h2')
            add_to_host_collection = PF5OUIAButton('add-to-a-host-collection-button')

            assigned_host_collections = HostColectionsList()

        @View.nested
        class recent_jobs(Card):
            ROOT = './/div[@data-ouia-component-id="card-template-Recent jobs"]'
            actions = Dropdown(locator='.//div[contains(@class, "pf-v5-c-dropdown")]')

            class finished(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

            class running(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

            class scheduled(Tab):
                table = SatTableWithoutHeaders(locator='.//table[@aria-label="recent-jobs-table"]')

        @View.nested
        class system_purpose(Card):
            ROOT = './/div[@data-ouia-component-id="system-purpose-card"]'
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
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-System properties")]'

            sys_properties = HostDetailsCard()

        @View.nested
        class operating_system(Card):
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-Operating system")]'

            architecture = Text(
                './/a[contains(@data-ouia-component-id, "host-architecture-button")]'
            )
            os = Text('.//a[contains(@data-ouia-component-id, "host-os-button")]')

            details = HostDetailsCard()

        @View.nested
        class provisioning(Card):
            ROOT = './/div[@data-ouia-component-type="PF5/Card" and .//div[text()="Provisioning"]]'

            details = HostDetailsCard()

        @View.nested
        class bios(Card):
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-BIOS")]'

            details = HostDetailsCard()

        @View.nested
        class registration_details(Card):
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-Registration details")]'

            details = HostDetailsCard()

        @View.nested
        class hw_properties(Card):
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-HW properties")]'

            details = HostDetailsCard()

        @View.nested
        class provisioning_templates(Card):
            ROOT = (
                './/div[contains(@data-ouia-component-id, "card-template-Provisioning templates")]'
            )

            templates_table = SatTableWithoutHeaders(
                locator='.//table[@aria-label="templates table"]'
            )

        @View.nested
        class installed_products(Card):
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-Installed products")]'

            installed_products_list = ItemsList(locator='.//ul[contains(@class, "pf-v5-c-list")]')

        @View.nested
        class networking_interfaces(Card):
            ROOT = (
                './/div[contains(@data-ouia-component-id, "card-template-Networking interfaces")]'
            )

            networking_interfaces_accordion = Accordion(
                locator='.//div[contains(@class, "pf-v5-c-card__expandable-content")]'
            )
            locator_templ = (
                './/div[contains(@class, "pf-v5-c-accordion__expanded-content-body")]'
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
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-Virtualization")]'

            details = HostDetailsCard()

        @View.nested
        class bootc(Card):
            # Will file issue for this to be fixed
            ROOT = './/div[contains(@data-ouia-component-id, "card-template-image-mode")]'

            remote_execution_link = Text(".//a[normalize-space(.)='Modify via remote execution']")
            details = HostDetailsCard()

        @View.nested
        class cloud_billing_details(Card):
            ROOT = (
                '//div[contains(@data-ouia-component-id, "card-template-GCP") '
                'or contains(@data-ouia-component-id, "card-template-AWS") '
                'or contains(@data-ouia-component-id, "card-template-Azure")]'
            )

            details = HostDetailsCard()

    @View.nested
    class content(PF5Tab):
        # TODO Setting ROOT is just a workaround because of BZ 2119076,
        # once this gets fixed we should use the parametrized locator from Tab class
        ROOT = './/div'
        transient_install_alert = PF5OUIAAlert('image-mode-alert-info')

        @View.nested
        class packages(PF5Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="packages-tab"]'

            select_all = Checkbox(
                locator='.//input[@data-ouia-component-id="select-all-checkbox-dropdown-toggle-checkbox"]'
            )
            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-v5-c-text-input-group__text-input")]'
            )
            status_filter = Dropdown(locator='.//div[@aria-label="select Status container"]/div')
            upgrade = Pf4ActionsDropdown(locator='.//div[div/button[normalize-space(.)="Upgrade"]]')
            dropdown = PF5Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')
            no_matching_packages = Text(
                './/h2[contains(@class, "pf-v5-c-empty-state__title-text")]'
            )

            table = PF5OUIATable(
                component_id='host-packages-table',
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Package': Text('./parent::td'),
                    'Status': Text('./span'),
                    'Installed version': Text('./parent::td'),
                    'Upgradable to': Text('./span'),
                    5: MenuToggleButtonMenu(),
                },
            )
            pagination = PF4Pagination()

        @View.nested
        class errata(PF5Tab):
            # workaround for BZ 2119076
            ROOT = './/div[@id="errata-tab"]'

            select_all = Checkbox(locator='.//div[@id="selection-checkbox"]/div/label')
            searchbar = SearchInput(locator='.//input[contains(@class, "pf-v5-c-text-input")]')
            type_filter = PF5OUIASelect(component_id='select Type')
            severity_filter = PF5OUIASelect(component_id='select Severity')
            apply = Pf4ActionsDropdown(locator='.//div[@aria-label="errata_dropdown"]')
            dropdown = PF5Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = PF5OUIAExpandableTable(
                component_id='host-errata-table',
                column_widgets={
                    1: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Errata': Text('./a'),
                    'Type': Text('./span'),
                    'Severity': Text('./span'),
                    'Installable': Text('./span'),
                    'Synopsis': Text('./span'),
                    'Published date': Text('./span/span'),
                    8: MenuToggleButtonMenu(),
                },
            )
            pagination = PF5Pagination()

        @View.nested
        class module_streams(PF5Tab):
            TAB_NAME = 'Module streams'
            # workaround for BZ 2119076
            ROOT = './/div[@id="modulestreams-tab"]'

            searchbar = SearchInput(
                locator='.//input[contains(@class, "pf-v5-c-text-input-group__text-input")]'
            )
            status_filter = PF5OUIASelect(component_id='select Status')
            installation_status_filter = PF5OUIASelect(component_id='select Installation status')
            dropdown = PF5Dropdown(locator='.//div[button[@aria-label="bulk_actions"]]')

            table = PF5OUIATable(
                component_id='host-module-stream-table',
                column_widgets={
                    'Name': Text('./a'),
                    'State': Text('.//span'),
                    'Stream': Text('./parent::td'),
                    'Installation status': Text('.//small'),
                    'Installed profile': Text('./parent::td'),
                    5: MenuToggleButtonMenu(),
                },
            )
            pagination = PF5Pagination()

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
            repository_type = PF5OUIASelect('select Repository type')
            dropdown = PF5OUIADropdown('repository-sets-bulk-actions')

            table = PF5OUIATable(
                component_id='host-repository-sets-table',
                column_widgets={
                    0: Checkbox(locator='.//input[@type="checkbox"]'),
                    'Repository': Text('./span'),
                    'Product': Text('./a'),
                    'Repository path': Text('./span'),
                    'Status': Text('.//span[contains(@class, "pf-v5-c-label__content")]'),
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
            locator='//div[@data-ouia-component-id="parameters-table-toolbar"]//input[contains(@class,"pf-v5-c-text-input-group__text-input")]'
        )
        parameter_name_input = TextInput(locator='.//td//input[contains(@aria-label, "name")]')
        parameter_type_input = Select(
            locator='.//td[2]//div[@data-ouia-component-type="PF4/Select"]'
        )
        parameter_value_input = TextInput(locator='.//td[3]//textarea')
        cancel_addition = Button(locator='.//td[5]//button[1]')
        confirm_addition = Button(locator='.//td[5]//button[2]')

        table_header = PF5OUIATable(component_id='parameters-table')
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
                5: MenuToggleButtonMenu(),
            },
        )
        pagination = PF5Pagination()

    @View.nested
    class traces(PF5Tab):
        ROOT = './/div'

        title = Text('//h2')
        enable_traces = PF5OUIAButton('enable-traces-button')
        select_all = Checkbox(locator='.//input[contains(@aria-label, "Select all")]')
        searchbar = SearchInput(locator='.//input[contains(@aria-label, "Select all")]')
        Pf4ActionsDropdown = PF5Button(
            locator='.//div[contains(@aria-label, "bulk_actions_dropdown")]'
        )
        traces_table = PatternflyTable(
            component_id='host-traces-table',
            column_widgets={
                0: Checkbox(locator='.//input[contains(@aria-label, "Select row")]'),
                'Application': Text('.//td[2]'),
                'Type': Text('.//td[3]'),
                'Helper': Text('.//td[4]'),
                4: PF5Button(locator='.//button[contains(@aria-label, "Actions")]'),
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
            edit = PF5Button(locator='.//button[@aria-label="edit ansible roles"]')
            noRoleAssign = Text('.//h5[contains(@class, "pf-v5-c-empty-state__title-text")]')
            table = PF5OUIATable(
                component_id='table-composable-compact',
                column_widgets={'Name': Text('.//a')},
            )
            pagination = PF4Pagination()

        @View.nested
        class variables(PF5Tab):
            TAB_NAME = 'Variables'
            ROOT = './/div[@class="ansible-host-detail"]'

            actions = PF5Button(locator='//button[contains(@aria-label, "Kebab toggle")]')
            delete = PF5Button(locator='//button[@role="menuitem"]')
            confirm = PF5Button(locator='//button[@data-ouia-component-id="btn-modal-confirm"]')
            table = PF5OUIATable(
                component_id='table-composable-compact',
                column_widgets={
                    'Name': Text('.//a'),
                    'Ansible role': Text('./span'),
                    'Type': Text('./span'),
                    # the next field can also be a form group
                    'Value': TextInput(
                        locator='//textarea[contains(@aria-label, "Edit override field")]'
                    ),
                    'Source attribute': Text('./span'),
                    # The next 2 buttons are hidden by default, but appear in this order
                    6: PF5Button(locator='.//button[@aria-label="Cancel editing override button"]'),
                    7: PF5Button(locator='.//button[@aria-label="Submit override button"]'),
                    # Clicking this button hides it, and displays the previous 2
                    5: PF5Button(locator='.//button[@aria-label="Edit override button"]'),
                },
            )
            table1 = PF5OUIATable(
                component_id='table-composable-compact',
                column_widgets={
                    5: PF5Button(locator='.//button[@aria-label="Submit editing override button"]'),
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
                scheduleRecurringJob = PF5Button(
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
                    locator='.//div[contains(@class, "pf-v5-c-table)"]',
                    column_widgets={
                        'Description': Text('.//a'),
                        'Schedule': Text('./span'),
                        'Next Run': Text('./span'),
                        4: Dropdown(locator='.//div[contains(@class, "pf-v5-c-dropdown")]'),
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
                7: PF5Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = PF4Pagination()

        @View.nested
        class enc_preview(PF5Tab):
            ROOT = './/div[@class="enc-preview-tab"]'
            TAB_NAME = 'ENC Preview'
            preview = Text('.//code')

        @View.nested
        class puppet_details(Card):
            ROOT = './/article[.//div[text()="Puppet details"]]'
            puppet_environment = Text(
                './div[2]//div[contains(@class, "pf-v5-c-description-list__group")][1]//dd'
            )
            puppet_capsule = Text(
                './div[2]//div[contains(@class, "pf-v5-c-description-list__group")][2]//dd'
            )
            puppet_ca_capsule = Text(
                './div[2]//div[contains(@class, "pf-v5-c-description-list__group")][3]//dd'
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
                8: PF5Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )

        pagination = PF4Pagination()

    @View.nested
    class insights(PF5Tab):
        ROOT = './/div'

        TAB_NAME = 'Recommendations'

        search_bar = SearchInput(locator='.//input[contains(@class, "pf-v5-c-text-input")]')
        remediate = PF5Button(locator='.//button[text()="Remediate"]')
        insights_dropdown = Dropdown(locator='.//div[contains(@class, "insights-dropdown")]')

        select_all_one_page = Checkbox(locator='.//input[@name="check-all"]')
        select_all_pages = PF5Button(
            locator='.//button[text()="Select recommendations from all pages"]'
        )

        recommendations_table = PF5OUIATable(
            component_id='rh-cloud-recommendations-table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Recommendation': Text('.//td[2]'),
                'Total Risk': Text('.//td[3]'),
                'Remediate': Text('.//td[4]'),
                4: PF5Button(locator='.//button[contains(@aria-label, "Actions")]'),
            },
        )
        pagination = PF5Pagination()

    @View.nested
    class iop_recommendations(PF5Tab):
        ROOT = './/div'

        TAB_NAME = 'Recommendations'

        search_field = TextInput(locator=('.//input[@aria-label="text input"]'))
        conditional_filter_dropdown = PF5Button(
            './/button[@data-ouia-component-id="ConditionalFilterToggle"]'
        )
        remediate = PF5Button('Remediate')
        download_playbook = PF5Button('Download playbook')
        bulk_select = BulkSelectMenuToggle()

        recommendations_table = PF5ExpandableTable(
            locator='.//table[contains(@data-ouia-component-id, "system-advisor-table")]',
            column_widgets={
                0: PF5Button('.//button[@aria-label="Details"]'),
                1: Checkbox(locator='.//input[@type="checkbox"]'),
                'Description': Text('.//span'),
                'Modified': Text('.//span'),
                'First impacted': Text('.//span'),
                'Total risk': Text('.//span'),
                'Remediation type': Text('.//span'),
            },
        )
        pagination = PF5Pagination()

        @property
        def is_displayed(self):
            return self.recommendations_table.is_displayed

    @View.nested
    class vulnerabilities(PF5Tab):
        ROOT = './/div'

        search_bar = SearchInput(locator='.//input[contains(@aria-label, "search-field")]')
        cve_menu_toggle = PF5Button(".//button[contains(@class, 'pf-v5-c-menu-toggle')]")
        no_cves_found_message = Text('.//h5[contains(@class, "pf-v5-c-empty-state__title-text")]')

        vulnerabilities_table = PF5ExpandableTable(
            # component_id='OUIA-Generated-Table-2',
            locator='.//table[contains(@class, "pf-v5-c-table")]',
            column_widgets={
                0: PF5Button(locator='.//button[@aria-label="Details"]'),
                'CVE ID': Text('.//td[contains(@data-label, "CVE ID")]'),
                'Publish date': Text('.//td[contains(@data-label, "Publish date")]'),
                'Severity': Text('.//td[contains(@data-label, "Severity")]'),
                'CVSS base score': Text('.//td[contains(@data-label, "CVSS base score")]'),
            },
        )
        pagination = PF5Pagination()

        @property
        def is_displayed(self):
            table_displayed = self.vulnerabilities_table.is_displayed
            no_cves_message_displayed = self.no_cves_found_message.is_displayed
            return table_displayed or no_cves_message_displayed


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

    install = PF5Button(locator='.//button[(normalize-space(.)="Install")]')
    cancel = PF5Button('Cancel')


class ContainerfileInstallCommandView(View):
    """Generate Containerfile Install Command modal"""

    ROOT = './/div[@data-ouia-component-id="containerfile-install-modal"]'

    unknown_persistence = PF5OUIASwitch('include-unknown-persistence-switch')
    command_description = PF5OUIAText('command-description-text')
    no_packages = PF5OUIAText('no-packages-text')

    command = TextInput(locator='.//input[@aria-label="Copyable input"]')
    cancel_button = PF5OUIAButton('cancel-button')


class AllAssignedRolesView(View):
    """All Assigned Roles Modal"""

    ROOT = './/div[@data-ouia-component-id="modal-ansible-roles"]'

    table = Table(
        locator='.//table[contains(@class, "pf-v5-c-table")]',
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

    confirm_delete = PF5OUIAButton('btn-modal-confirm')
    cancel_delete = PF5OUIAButton('btn-modal-cancel')


class ManageHostCollectionModal(View):
    """Host Collection Modal"""

    ROOT = './/div[@data-ouia-component-id="host-collections-modal"]'

    create_host_collection = OUIAButton('empty-state-primary-action-button')
    select_all = Checkbox(locator='.//input[contains(@aria-label, "Select all")]')
    searchbar = SearchInput(locator='.//input[contains(@class, "pf-m-search")]')

    host_collection_table = Table(
        locator='.//table[contains(@class, "pf-v5-c-table")]',
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
    close_modal = PF5Button(locator='.//button[@aria-label="Close"]')
    host_statuses_table = PF5OUIATable(
        component_id='statuses-table',
        column_widgets={
            'Name': Text('.//td[contains(@data-label, "Name")]'),
            'Status': Text('.//td[contains(@data-label, "Status")]'),
            'Reported at': Text('.//td[contains(@data-label, "Reported at")]'),
            3: PF5Button(locator='.//td[contains(@class, "action")]'),
        },
    )

    def read(self):
        # Parses into a dictionary of {name: {status, reported_at}}
        return {value.pop('Name'): value for value in self.host_statuses_table.read()}


class EditAnsibleRolesView(View):
    """Edit Ansible Roles Modal"""

    addAnsibleRole = DualListSelector('//div[@class = "pf-v5-c-dual-list-selector"]')
    confirm = PF5Button(locator='.//button[@aria-label="submit ansible roles"]')
    hostAssignedAnsibleRoles = Text(
        './/button[@class="pf-v5-c-dual-list-selector__item"]/span[1]//span[2]'
    )
    selectRoles = PF5Button(locator='.//button[@aria-label="Add selected"]')
    unselectRoles = PF5Button(locator='.//button[@aria-label="Remove selected"]')


class ModuleStreamDialog(Pf5ConfirmationDialog):
    confirm_dialog = PF5Button(locator='.//button[@aria-label="confirm-module-action"]')
    cancel_dialog = PF5Button(locator='.//button[@aria-label="cancel-module-action"]')


class RecurringJobDialog(Pf5ConfirmationDialog):
    confirm_dialog = PF5Button(locator='.//button[@data-ouia-component-id="btn-modal-confirm"]')
    cancel_dialog = PF5Button(locator='.//button[@data-ouia-component-id="btn-modal-cancel"]')


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
        CHECKBOX_SECTION_TOGGLE.format('Network'),
        CHECKBOX_SECTION_TOGGLE.format('Reported data'),
        CHECKBOX_SECTION_TOGGLE.format('Red Hat Lightspeed'),
        CHECKBOX_SECTION_TOGGLE.format('Content'),
    ]
    title = Text(
        './/header//span[contains(@class, "pf-v5-c-modal-box__title")]'
        '[normalize-space(.)="Manage columns"]'
    )
    confirm_dialog = PF5Button(locator='.//button[normalize-space(.)="Save"]')
    cancel_dialog = PF5Button(locator='.//button[normalize-space(.)="Cancel"]')
    checkbox_group = PF5CheckboxTreeView(locator='.//div[contains(@class, "pf-v5-c-tree-view")]')

    def collapsed_sections(self):
        return (self.browser.element(locator) for locator in self.DEFAULT_COLLAPSED_SECTIONS)

    def get_tree_sections_state(self):
        sections = self.browser.selenium.find_elements(
            By.XPATH, '//div[@class="pf-v5-c-tree-view"]/ul/li'
        )

        expanded = []
        collapsed = []

        for section in sections:
            # Get the label text
            label = section.find_element(
                By.XPATH, './/span[contains(@class,"pf-v5-c-tree-view__node-text")]'
            ).text.strip()

            state = section.get_attribute('aria-expanded')

            if state == 'true':
                expanded.append(label)
            elif state == 'false':
                collapsed.append(label)
            else:
                # No aria-expanded means it`s a leaf node
                collapsed.append(label)

        return expanded, collapsed

    def sections_state(self):
        expanded, collapsed = self.get_tree_sections_state()
        return {'expanded': expanded, 'collapsed': collapsed}

    @property
    def is_displayed(self):
        return self.title.is_displayed

    def expand_all(self):
        """Expand all tree sections that are collapsed"""
        sections_state = self.sections_state()
        if sections_state['collapsed'] != []:
            for section in sections_state['collapsed']:
                section_toggle_to_expand_xpath = self.CHECKBOX_SECTION_TOGGLE.format(section)
                self.browser.element(section_toggle_to_expand_xpath).click()

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


class NewCVEnvAssignmentSection(PF5LCESelectorGroup):
    # Generic ROOT that works for both new and existing assignments
    # Don't check for "Select a content view" text - just find the assignment-section div
    ROOT = (
        './/div[contains(@class,"pf-v5-c-expandable-section") and contains(@class,"pf-m-expanded")]'
    )

    PARAMETERS = ('lce_name',)

    lce_selector = PF5LCESelector(
        locator=ParametrizedLocator(
            './/input[@type="radio"][following-sibling::label//span[normalize-space(.)="{lce_name}"]]'
        )
    )
    content_source_select = CVESelect()


class ManageMultiCVEnvModal(PF5Modal):
    """
    This class represents the 'Assign content view environments' modal on the host overview page
    when the 'Allow multiple content views' setting is enabled.
    """

    ROOT = './/div[@data-ouia-component-id="assign-cv-modal" or @data-ouia-component-id="bulk-assign-cves-modal"]'

    title = Text('//span[normalize-space(.)="Assign content view environments"]')
    assign_cv_btn = PF5OUIAButton('assign-another-cv-button')
    save_btn = PF5Button(
        locator='.//button[@data-ouia-component-id="assign-cv-modal-save-button" or @data-ouia-component-id="bulk-assign-cves-modal-save-button"]'
    )
    cancel_btn = PF5Button(
        locator='.//button[@data-ouia-component-id="assign-cv-modal-cancel-button" or @data-ouia-component-id="bulk-assign-cves-modal-cancel-button"]'
    )
    new_assignment_section = ParametrizedView.nested(NewCVEnvAssignmentSection)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
