from widgetastic.widget import Checkbox, ParametrizedView, Text, View
from widgetastic_patternfly4 import (
    Button,
    Dropdown,
    Menu,
    Modal,
    Pagination,
    Radio,
    Select,
)
from widgetastic_patternfly4.ouia import (
    Alert as OUIAAlert,
    PatternflyTable,
)

from airgun.views.common import (
    BaseLoggedInView,
    PF4LCESelectorGroup,
    SearchableViewMixinPF4,
    WizardStepView,
)
from airgun.views.host_new import ManageColumnsView, PF4CheckboxTreeView
from airgun.widgets import ItemsList, SearchInput


class AllHostsMenu(Menu):
    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-menu-toggle')]"
    ROOT = f"{BUTTON_LOCATOR}/.."


class AllHostsSelect(Select):
    BUTTON_LOCATOR = ".//button[@aria-label='Options menu']"
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-c-select__menu')]/li"
    ITEM_LOCATOR = (
        "//*[contains(@class, 'pf-c-select__menu-item') and .//*[contains(normalize-space(.), {})]]"
    )
    SELECTED_ITEM_LOCATOR = ".//span[contains(@class, 'ins-c-conditional-filter')]"
    TEXT_LOCATOR = ".//div[contains(@class, 'pf-c-select') and child::button]"
    DEFAULT_LOCATOR = (
        './/div[contains(@class, "pf-c-select") and @data-ouia-component-id="select-content-view"]'
    )


class CVESelect(Select):
    BUTTON_LOCATOR = ".//button[@aria-label='Options menu']"
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-c-select__menu')]/li"
    ITEM_LOCATOR = (
        "//*[contains(@class, 'pf-c-select__menu-item') and .//*[contains(normalize-space(.), {})]]"
    )
    SELECTED_ITEM_LOCATOR = ".//span[contains(@class, 'ins-c-conditional-filter')]"
    TEXT_LOCATOR = ".//div[contains(@class, 'pf-c-select') and child::button]"
    DEFAULT_LOCATOR = (
        './/div[contains(@class, "pf-c-select") and @data-ouia-component-id="select-content-view"]'
    )


class AllHostsTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Hosts']")
    select_all = Checkbox(
        locator='.//input[@data-ouia-component-id="select-all-checkbox-dropdown-toggle-checkbox"]'
    )
    bulk_actions = AllHostsMenu()
    bulk_actions_kebab = Button(locator='.//button[@aria-label="plain kebab"]')
    bulk_actions_menu = Menu(locator='.//div[@data-ouia-component-id="hosts-index-actions-kebab"]')

    table_loading = Text("//h5[normalize-space(.)='Loading']")
    no_results = Text("//h5[normalize-space(.)='No Results']")
    manage_columns = Button("Manage columns")
    table = PatternflyTable(
        component_id='table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Name': Text('./a'),
            2: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
        },
    )
    alert_message = Text('.//div[@aria-label="Success Alert" or @aria-label="Danger Alert"]')

    pagination = Pagination()

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.table_loading, exception=False) is None
            and self.browser.wait_for_element(self.table, exception=False) is not None
        )


class HostDeleteDialog(View):
    """Confirmation dialog for deleting host"""

    ROOT = './/div[@data-ouia-component-id="app-confirm-modal"]'

    title = Text("//span[normalize-space(.)='Delete host?']")

    confirm_delete = Button(locator='//button[normalize-space(.)="Delete"]')
    cancel_delete = Button(locator='//button[normalize-space(.)="Cancel"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class BuildManagementDialog(View):
    """Dialog for Build Management"""

    ROOT = './/div[@data-ouia-component-id="bulk-build-hosts-modal"]'

    title = Text(".//h1[normalize-space(.)='Build management']")

    build = Radio(locator='.//input[@data-ouia-component-id="build-host-radio"]')
    reboot_now = Checkbox(locator='.//input[@data-ouia-component-id="build-reboot-checkbox"]')
    rebuild_provisioning_only = Checkbox(
        locator='.//input[@data-ouia-component-id="rebuild-host-radio"]'
    )

    confirm = Button(locator='//button[normalize-space(.)="Confirm"]')
    cancel = Button(locator='//button[normalize-space(.)="Cancel"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class BulkHostDeleteDialog(View):
    """Confirmation dialog for bulk deleting hosts or hosts with compute resources"""

    ROOT = './/div[@id="bulk-delete-hosts-modal"]'

    title = Text("//span[normalize-space(.)='Delete hosts?']")
    confirm_checkbox = Checkbox(locator='.//input[@id="dire-warning-checkbox"]')

    confirm_delete = Button(locator='//button[normalize-space(.)="Delete"]')
    cancel_delete = Button(locator='//button[normalize-space(.)="Cancel"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class HostgroupDialog(View):
    """Dialog for bulk changing Hosts' assigned hostgroup"""

    ROOT = './/div[@id="bulk-reassign-hg-modal"]'

    title = Text("//span[normalize-space(.)='Change host group']")
    hostgroup_dropdown = AllHostsSelect(
        locator='.//div[contains(@class, "pf-c-select") and @data-ouia-component-id="select-host-group"]'
    )

    save_button = Button(locator='//button[normalize-space(.)="Save"]')
    cancel_button = Button(locator='//button[normalize-space(.)="Cancel"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class AllHostsCheckboxTreeView(PF4CheckboxTreeView):
    """Small tweaks to work with All Hosts"""

    CHECKBOX_LOCATOR = './/*[self::span|self::label][contains(@class, "pf-c-tree-view__node-text")]/preceding-sibling::span/input[@type="checkbox"]'


class AllHostsManageColumnsView(ManageColumnsView):
    """Manage columns modal from Hosts page, small tweaks to work with All Hosts"""

    ROOT = './/div[@data-ouia-component-id="manage-columns-modal"]'

    def read(self):
        """
        Get labels and values of all checkboxes in the dialog.

        :return dict: mapping of `label: value` items
        """
        return self.checkbox_group.read()

    def fill(self, values):
        """
        Overwritten to ignore the "Expand tree" functionality
        """
        self.checkbox_group.fill(values)


class ManageCVEModal(Modal):
    """
    This class represents the Manage Content View Environments modal that is used to update the CVE of hosts.
    """

    ROOT = './/div[@data-ouia-component-id="bulk-change-host-cv-modal"]'

    title = Text("//span[normalize-space(.)='Edit content view environments']")
    save_btn = Button(locator='//button[normalize-space(.)="Save"]')
    cancel_btn = Button(locator='//button[normalize-space(.)="Cancel"]')
    content_source_select = AllHostsSelect()
    lce_selector = ParametrizedView.nested(PF4LCESelectorGroup)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ManagePackagesModal(Modal):
    """
    This class represents the Manage Packages modal that is used to install or update packages on hosts.
    It contains severeal nested views that represent the steps of the wizard.
    """

    OUIA_ID = 'bulk-packages-wizard-modal'

    title = './/h2[@data-ouia-component-type="PF4/Title"]'
    close_btn = Button(locator='//button[@class="pf-c-button pf-m-plain pf-c-wizard__close"]')
    cancel_btn = Button(locator='//button[normalize-space(.)="Cancel"]')
    back_btn = Button(locator='//button[normalize-space(.)="Back"]')
    next_btn = Button(locator='//button[normalize-space(.)="Next"]')

    @View.nested
    class select_action(WizardStepView):
        expander = Text('.//button[text()="Select action"]')
        content_text = Text('.//div[@class="pf-c-content"]')

        upgrade_all_packages_radio = Radio(id='r1-upgrade-all-packages')
        upgrade_packages_radio = Radio(id='r2-upgrade-packages')
        install_packages_radio = Radio(id='r3-install-packages')
        remove_packages_radio = Radio(id='r4-remove-packages')

    @View.nested
    class upgrade_packages(WizardStepView):
        locator_prefix = '//div[contains(., "Upgrade packages")]/descendant::'

        expander = Text('.//button[contains(.,"Upgrade packages")]')
        content_text = Text('.//div[@class="pf-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        clear_search = Button(locator=f'{locator_prefix}button[@aria-label="Reset search"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Package': Text('.//td[2]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class install_packages(WizardStepView):
        locator_prefix = './/div[contains(., "Install packages")]/descendant::'

        expander = Text('.//button[contains(.,"Install packages")]')
        content_text = Text('.//div[@class="pf-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        clear_search = Button(locator=f'{locator_prefix}button[@aria-label="Reset search"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Package': Text('.//td[2]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class remove_packages(WizardStepView):
        locator_prefix = './/div[contains(., "Remove packages")]/descendant::'

        expander = Text('.//button[contains(.,"Remove packages")]')
        content_text = Text('.//div[@class="pf-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        clear_search = Button(locator=f'{locator_prefix}button[@aria-label="Reset search"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Package': Text('.//td[2]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class review_hosts(WizardStepView):
        locator_prefix = './/div[contains(.,"Review hosts")]/descendant::'

        expander = Text('.//button[contains(.,"Review hosts")]')
        content_text = Text('.//div[@class="pf-c-content"]')
        error_message = OUIAAlert('no-hosts-alert')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//td[2]'),
                'OS': Text('.//td[3]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class review(WizardStepView):
        expander = Text('.//button[text()="Review"]')
        content_text = Text('.//div[@class="pf-c-content"]')

        tree_expander_packages = Button(
            './/button[@class="pf-c-tree-view__node" and contains(.,"Packages to")]'
        )
        expanded_package_list = ItemsList(
            locator='//ul[@class="pf-c-tree-view__list" and @role="tree"][1]'
        )
        # using wording manage instead of install and update, because in UI
        # it changes based on the selected action but generally it looks the same
        # Returns 'All' or number of packages to manage
        number_of_packages_to_manage = Text(
            '''.//span[contains(.,"Packages to")]/following-sibling::span/span[@class="pf-c-badge pf-m-read"]'''
        )

        edit_selected_packages = Button('.//button[@aria-label="Edit packages list"]')
        # Returns number of hosts to manage
        number_of_hosts_to_manage = Text(
            '''.//span[contains(.,"Hosts")]/following-sibling::span/span[@class="pf-c-badge pf-m-read"]'''
        )
        edit_selected_hosts = Button('.//button[@aria-label="Edit host selection"]')
        manage_via_dropdown = Dropdown(
            locator='//div[@data-ouia-component-id="bulk-packages-wizard-dropdown"]'
        )
        finish_package_management_btn = Button(
            locator='//*[@data-ouia-component-type="PF4/Button" and (normalize-space(.)="Install" or normalize-space(.)="Upgrade" or normalize-space(.)="Remove")]'
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ManageErrataModal(Modal):
    """
    This class represents the Manage Errata modal that is used to apply errata on hosts.
    It contains several nested views that represent the steps of the wizard.
    """

    OUIA_ID = 'bulk-errata-wizard-modal'

    title = './/h2[@data-ouia-component-type="PF4/Title"]'
    close_btn = Button(locator='//button[@class="pf-c-button pf-m-plain pf-c-wizard__close"]')
    cancel_btn = Button(locator='//button[normalize-space(.)="Cancel"]')
    back_btn = Button(locator='//button[normalize-space(.)="Back"]')
    next_btn = Button(locator='//button[normalize-space(.)="Next"]')

    @View.nested
    class select_errata(WizardStepView):
        wizard_step_name = "Select errata"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'
        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        clear_search = Button(locator=f'{locator_prefix}button[@aria-label="Reset search"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Erratum': Text('.//td[2]'),
                'Title': Text('.//td[3]'),
                'Type': Text('.//td[4]'),
                'Severity': Text('.//td[5]'),
                'Affected hosts': Text('.//td[6]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class review_hosts(WizardStepView):
        wizard_step_name = "Review hosts"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'

        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-c-content"]')
        error_message = OUIAAlert('no-hosts-alert')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(locator=f'{locator_prefix}input[@aria-label="Search input"]')
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PatternflyTable(
            component_id='table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//td[2]'),
                'OS': Text('.//td[3]'),
            },
        )
        pagination = Pagination()

    @View.nested
    class review(WizardStepView):
        wizard_step_name = "Review"
        expander = Text(f'.//button[text()="{wizard_step_name}"]')

        tree_expander_errata = Button(
            './/button[@class="pf-c-tree-view__node" and contains(.,"Errata to")]'
        )
        expanded_errata_list = ItemsList(
            locator='//ul[@class="pf-c-tree-view__list" and @role="tree"][1]'
        )

        number_of_errata_to_manage = Text(
            '''.//span[contains(.,"Errata to")]/following-sibling::span/span[@class="pf-c-badge pf-m-read"]'''
        )

        edit_selected_errata = Button('.//button[@aria-label="Edit errata list"]')
        # Returns number of hosts to manage
        number_of_hosts_to_manage = Text(
            '''.//span[contains(.,"Hosts")]/following-sibling::span/span[@class="pf-c-badge pf-m-read"]'''
        )
        edit_selected_hosts = Button('.//button[@aria-label="Edit host selection"]')
        manage_via_dropdown = Dropdown(
            locator='//div[@data-ouia-component-id="bulk-errata-wizard-dropdown"]'
        )

        finish_errata_management_btn = Button(
            locator='//*[@data-ouia-component-type="PF4/Button" and normalize-space(.)="Apply"]'
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
