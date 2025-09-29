from widgetastic.widget import Checkbox, ParametrizedView, Text, View
from widgetastic_patternfly4 import (
    Button,
    Dropdown,
    ExpandableTable,
    Pagination,
    Radio,
    Select,
)
from widgetastic_patternfly4.ouia import (
    Alert as OUIAAlert,
)
from widgetastic_patternfly5 import (
    Alert as PF5Alert,
    Button as PF5Button,
    Dropdown as PF5Dropdown,
    Menu as PF5Menu,
    Modal as PF5Modal,
    Radio as PF5Radio,
    Select as PF5Select,
)
from widgetastic_patternfly5.ouia import (
    Button as PF5OUIAButton,
    PatternflyTable as PF5OUIATable,
)

from airgun.views.common import (
    BaseLoggedInView,
    PF5LCESelectorGroup,
    SearchableViewMixinPF4,
    WizardStepView,
)
from airgun.views.host_new import ManageColumnsView, PF5CheckboxTreeView
from airgun.widgets import ItemsList, SearchInput


class MenuToggleDropdownInTable(PF5Dropdown):
    """
    This class is PF5 implementation of dropdown component within the table row.
    Which is MenuToggle->Dropdown and not just Dropdown as it was in PF4.
    """

    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-v5-c-menu-toggle')]"
    DEFAULT_LOCATOR = './/div[contains(@class, "pf-v5-c-menu") and @data-ouia-component-id="PF5/Dropdown"]'
    ROOT = f"{BUTTON_LOCATOR}/.."
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-v5-c-menu__list')]/li"
    ITEM_LOCATOR = "//*[contains(@class, 'pf-v5-c-menu__item') and .//*[contains(normalize-space(.), {})]]"


class AllHostsSelect(Select):
    BUTTON_LOCATOR = ".//button[@aria-label='Options menu']"
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-c-select__menu')]/li[contains(@class, 'pf-c-select__menu-wrapper')]"
    ITEM_LOCATOR = '//*[contains(@class, "pf-c-select__menu-item") and contains(normalize-space(.), {})]'
    SELECTED_ITEM_LOCATOR = ".//span[contains(@class, 'ins-c-conditional-filter')]"
    TEXT_LOCATOR = ".//div[contains(@class, 'pf-c-select') and child::button]"


class AllHostsMenu(PF5Menu):
    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-v5-c-menu-toggle')]"
    ROOT = f"{BUTTON_LOCATOR}/.."


class CVESelect(Select):
    BUTTON_LOCATOR = './/button[@aria-label="Options menu"]'
    ITEMS_LOCATOR = './/ul[contains(@class, "pf-v5-c-select__menu")]/li'
    ITEM_LOCATOR = '//*[contains(@class, "pf-v5-c-select__menu-item") and .//*[contains(normalize-space(.), {})]]'
    SELECTED_ITEM_LOCATOR = './/span[contains(@class, "ins-c-conditional-filter")]'
    TEXT_LOCATOR = './/div[contains(@class, "pf-v5-c-select") and child::button]'
    DEFAULT_LOCATOR = './/div[contains(@class, "pf-v5-c-select") and @data-ouia-component-id="select-content-view"]'


class AllHostsTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Hosts']")

    legacy_kebab = PF5Dropdown(locator='.//div[@id="legacy-ui-kebab"]')
    select_all = Checkbox(
        locator='.//input[@data-ouia-component-id="select-all-checkbox-dropdown-toggle-checkbox"]'
    )
    top_bulk_actions = MenuToggleDropdownInTable(
        locator='.//button[@aria-label="plain kebab"]'
    )
    bulk_actions = AllHostsMenu()
    bulk_actions_kebab = Button(locator='.//button[@aria-label="plain kebab"]')
    bulk_actions_menu = PF5Menu(
        locator='.//div[@data-ouia-component-id="hosts-index-actions-kebab"]'
    )
    bulk_actions_manage_content_menu = PF5Menu(
        locator='//li[contains(@class, "pf-v5-c-menu__list-item")]//button[span/span[text()="Manage content"]]/following-sibling::div[contains(@class, "pf-v5-c-menu")]'
    )
    bulk_actions_change_associations_menu = PF5Menu(
        locator='//li[contains(@class, "pf-v5-c-menu__list-item")]//button[span/span[text()="Change associations"]]/following-sibling::div[contains(@class, "pf-v5-c-menu")]'
    )

    table_loading = Text("//h5[normalize-space(.)='Loading']")
    no_results = Text("//h5[normalize-space(.)='No Results']")
    manage_columns = PF5Button("Manage columns")
    table = PF5OUIATable(
        component_id="table",
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            "Name": Text("./a"),
            2: MenuToggleDropdownInTable(),
        },
    )
    alert_message = Text('.//div[contains(@class, "pf-v5-c-alert")]')

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
    reboot_now = Checkbox(
        locator='.//input[@data-ouia-component-id="build-reboot-checkbox"]'
    )
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


class AllHostsCheckboxTreeView(PF5CheckboxTreeView):
    """Small tweaks to work with All Hosts"""

    CHECKBOX_LOCATOR = './/*[self::span|self::label][contains(@class, "pf-v5-c-tree-view__node-text")]/preceding-sibling::span/input[@type="checkbox"]'


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


class ManageCVEModal(PF5Modal):
    """
    This class represents the Manage Content View Environments modal that is used to update the CVE of hosts.
    """

    ROOT = './/div[@data-ouia-component-id="bulk-change-host-cv-modal"]'

    title = Text("//span[normalize-space(.)='Edit content view environments']")
    save_btn = Button(locator='//button[normalize-space(.)="Save"]')
    cancel_btn = Button(locator='//button[normalize-space(.)="Cancel"]')
    content_source_select = CVESelect()
    lce_selector = ParametrizedView.nested(PF5LCESelectorGroup)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ManagePackagesModal(PF5Modal):
    """
    This class represents the Manage Packages modal that is used to install or update packages on hosts.
    It contains severeal nested views that represent the steps of the wizard.
    """

    OUIA_ID = "bulk-packages-wizard-modal"

    title = './/h2[@data-ouia-component-type="PF4/Title"]'
    close_btn = PF5Button(
        locator='//button[@class="pf-v5-c-button pf-m-plain pf-v5-c-wizard__close"]'
    )
    cancel_btn = PF5Button(locator='//button[normalize-space(.)="Cancel"]')
    back_btn = PF5Button(locator='//button[normalize-space(.)="Back"]')
    next_btn = PF5Button(locator='//button[normalize-space(.)="Next"]')

    @View.nested
    class select_action(WizardStepView):
        expander = Text('.//button[text()="Select action"]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        upgrade_all_packages_radio = PF5Radio(id="r1-upgrade-all-packages")
        upgrade_packages_radio = PF5Radio(id="r2-upgrade-packages")
        install_packages_radio = PF5Radio(id="r3-install-packages")
        remove_packages_radio = PF5Radio(id="r4-remove-packages")

    @View.nested
    class upgrade_packages(WizardStepView):
        locator_prefix = '//div[contains(., "Upgrade packages")]/descendant::'

        expander = Text('.//button[contains(.,"Upgrade packages")]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        clear_search = Button(
            locator=f'{locator_prefix}button[@aria-label="Reset search"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Package": Text(".//td[2]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class install_packages(WizardStepView):
        locator_prefix = './/div[contains(., "Install packages")]/descendant::'

        expander = Text('.//button[contains(.,"Install packages")]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        clear_search = Button(
            locator=f'{locator_prefix}button[@aria-label="Reset search"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Package": Text(".//td[2]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class remove_packages(WizardStepView):
        locator_prefix = './/div[contains(., "Remove packages")]/descendant::'

        expander = Text('.//button[contains(.,"Remove packages")]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        clear_search = Button(
            locator=f'{locator_prefix}button[@aria-label="Reset search"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Package": Text(".//td[2]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class review_hosts(WizardStepView):
        locator_prefix = './/div[contains(.,"Review hosts")]/descendant::'

        expander = Text('.//button[contains(.,"Review hosts")]')
        content_text = Text('.//p[@data-ouia-component-id="mpw-step-3-content"]')
        error_message = OUIAAlert("no-hosts-alert")

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Name": Text(".//td[2]"),
                "OS": Text(".//td[3]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class review(WizardStepView):
        expander = Text('.//button[text()="Review"]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        tree_expander_packages = Button(
            './/button[@class="pf-v5-c-tree-view__node" and contains(.,"Packages to")]'
        )
        expanded_package_list = ItemsList(
            locator='//ul[@class="pf-v5-c-tree-view__list" and @role="tree"][1]'
        )
        # using wording manage instead of install and update, because in UI
        # it changes based on the selected action but generally it looks the same
        # Returns 'All' or number of packages to manage
        number_of_packages_to_manage = Text(
            """.//span[contains(.,"Packages to")]/following-sibling::span/span[@class="pf-v5-c-badge pf-m-read"]"""
        )

        edit_selected_packages = Button('.//button[@aria-label="Edit packages list"]')
        # Returns number of hosts to manage
        number_of_hosts_to_manage = Text(
            """.//span[contains(.,"Hosts")]/following-sibling::span/span[@class="pf-v5-c-badge pf-m-read"]"""
        )
        edit_selected_hosts = Button('.//button[@aria-label="Edit host selection"]')
        manage_via_dropdown = PF5Dropdown(
            locator='//div[@data-ouia-component-id="bulk-packages-wizard-dropdown"]'
        )
        finish_package_management_btn = PF5Button(
            locator='//*[@data-ouia-component-type="PF5/Button" and (normalize-space(.)="Install" or normalize-space(.)="Upgrade" or normalize-space(.)="Remove")]'
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ManageErrataModal(PF5Modal):
    """
    This class represents the Manage Errata modal that is used to apply errata on hosts.
    It contains several nested views that represent the steps of the wizard.
    """

    OUIA_ID = "bulk-errata-wizard-modal"

    title = './/h2[@data-ouia-component-type="PF4/Title"]'
    close_btn = PF5Button(
        locator='//button[@class="pf-v5-c-button pf-m-plain pf-v5-c-wizard__close"]'
    )
    cancel_btn = PF5Button(locator='//button[normalize-space(.)="Cancel"]')
    back_btn = PF5Button(locator='//button[normalize-space(.)="Back"]')
    next_btn = PF5Button(locator='//button[normalize-space(.)="Next"]')

    @View.nested
    class select_errata(WizardStepView):
        wizard_step_name = "Select errata"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'
        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        clear_search = Button(
            locator=f'{locator_prefix}button[@aria-label="Reset search"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Erratum": Text(".//td[2]"),
                "Title": Text(".//td[3]"),
                "Type": Text(".//td[4]"),
                "Severity": Text(".//td[5]"),
                "Affected hosts": Text(".//td[6]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class review_hosts(WizardStepView):
        wizard_step_name = "Review hosts"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'

        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-v5-c-content"]')
        error_message = OUIAAlert("no-hosts-alert")

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Name": Text(".//td[2]"),
                "OS": Text(".//td[3]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class review(WizardStepView):
        wizard_step_name = "Review"
        expander = Text(f'.//button[text()="{wizard_step_name}"]')

        tree_expander_errata = Button(
            './/button[@class="pf-v5-c-tree-view__node" and contains(.,"Errata to")]'
        )
        expanded_errata_list = ItemsList(
            locator='//ul[@class="pf-v5-c-tree-view__list" and @role="tree"][1]'
        )

        number_of_errata_to_manage = Text(
            """.//span[contains(.,"Errata to")]/following-sibling::span/span[@class="pf-v5-c-badge pf-m-read"]"""
        )

        edit_selected_errata = Button('.//button[@aria-label="Edit errata list"]')
        # Returns number of hosts to manage
        number_of_hosts_to_manage = Text(
            """.//span[contains(.,"Hosts")]/following-sibling::span/span[@class="pf-v5-c-badge pf-m-read"]"""
        )
        edit_selected_hosts = Button('.//button[@aria-label="Edit host selection"]')
        manage_via_dropdown = PF5Dropdown(
            locator='//div[@data-ouia-component-id="bulk-errata-wizard-dropdown"]'
        )

        finish_errata_management_btn = PF5Button(
            locator='//*[@data-ouia-component-type="PF5/Button" and normalize-space(.)="Apply"]'
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class RepositorySetsMenu(PF5Dropdown):
    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-v5-c-menu-toggle')]"
    DEFAULT_LOCATOR = PF5Button(
        locator='//td[@data-label="Status"]/button[contains(@class,"pf-v5-c-menu-toggle")]'
    )
    ROOT = f"{BUTTON_LOCATOR}/.."
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-v5-c-menu__list')]/li"
    ITEM_LOCATOR = '//*[contains(@class, "pf-v5-c-menu__item") and .//*[contains(normalize-space(.), {})]]'


class ManageRepositorySetsModal(PF5Modal):
    """
    This class represents the Manage Repository Sets modal that is used to apply content overrides actions
    on one or more repository.
    It contains several nested views that represent the steps of the wizard.
    """

    OUIA_ID = "bulk-repo-sets-wizard-modal"

    # Hidden alert - Change the status of at least one repository.
    repo_set_alert_icon = './/div[@class="pf-v5-c-alert__icon"]'
    repo_set_alert_msg_xpath = (
        f'{repo_set_alert_icon}/following-sibling::h4[@class="pf-v5-c-alert__title"]'
    )

    title = './/h2[@class="pf-v5-c-wizard__title-text"]'
    content_override_action_dropdown = Dropdown(
        locator='.//button[@data-ouia-component-id="OUIA-Generated-MenuToggle-primary-1"]'
    )

    close_btn = PF5Button(locator='.//div[@class="pf-v5-c-wizard__close"]')
    cancel_btn = PF5Button(locator='//button[normalize-space(.)="Cancel"]')
    back_btn = PF5Button(locator='//button[normalize-space(.)="Back"]')
    next_btn = PF5Button(locator='//button[normalize-space(.)="Next"]')

    @View.nested
    class select_repository_sets(WizardStepView):
        wizard_step_name = "Select repository sets"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'
        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-c-content"]')

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        clear_search = Button(
            locator=f'{locator_prefix}button[@aria-label="Reset search"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        no_change_status_dropdown = PF5Button(
            locator='//td[@data-label="Status"]/button[contains(@class,"pf-v5-c-menu-toggle")]'
        )

        status_options = PF5Dropdown(
            locator=".//ul[contains(@class, '-c-menu__list') or contains(@class, '-c-dropdown__menu')]/li"
        )

        table = ExpandableTable(
            locator='//div[@data-ouia-component-id="bulk-repo-sets-wizard-modal"]//table[@data-ouia-component-id="table"]',
            column_widgets={
                0: PF5Button(locator='.//button[@aria-label="Details"]'),
                1: Checkbox(locator='.//input[@type="checkbox"]'),
                "Name": Text(".//td[2]"),
                "Status": RepositorySetsMenu(),
            },
        )
        pagination = Pagination()

    @View.nested
    class review_hosts(WizardStepView):
        wizard_step_name = "Review hosts"
        locator_prefix = f'.//div[contains(., "{wizard_step_name}")]/descendant::'

        expander = Text(f'.//button[text()="{wizard_step_name}"]')
        content_text = Text('.//div[@class="pf-c-content"]')
        error_message = OUIAAlert("no-hosts-alert")

        select_all = Checkbox(locator=f'{locator_prefix}div[@id="selection-checkbox"]')
        search_input = SearchInput(
            locator=f'{locator_prefix}input[@aria-label="Search input"]'
        )
        search = Button(locator=f'{locator_prefix}button[@aria-label="Search"]')

        table = PF5OUIATable(
            component_id="table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                "Name": Text(".//td[2]"),
                "OS": Text(".//td[3]"),
            },
        )
        pagination = Pagination()

    @View.nested
    class review(WizardStepView):
        wizard_step_name = "Review"
        expander = Text(f'.//button[text()="{wizard_step_name}"]')

        number_of_repository_status_changed = Text(
            './/div/h4[contains(.,"Changed status")]/following::div/span[@class="pf-v5-c-badge pf-m-read"]'
        )

        edit_selected_repository_sets = Button(
            './/button[@data-ouia-component-id="brsw-review-step-edit-btn"]'
        )
        set_content_overrides = Button(
            locator='//button[@type="submit" and @data-ouia-component-id="bulk-repo-sets-wizard-finish-button"]'
        )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class DisassociateHostsModal(PF5Modal):
    """
    This class represents the Disassociate Hosts modal
    which is used to disassociate hosts from their UUID
    and compute_resource_id associations.
    """

    OUIA_ID = "bulk-disassociate-modal"

    title = './/h1[@class="pf-v5-c-modal-box__title"]'
    close_btn = PF5OUIAButton("bulk-disassociate-modal-ModalBoxCloseButton")
    confirm_btn = PF5OUIAButton("bulk-disassociate-modal-add-button")
    cancel_btn = PF5OUIAButton("bulk-disassociate-modal-cancel-button")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class MenuToggleSelect(PF5Select):
    """
    This class is PF5 implementation of the Select component within the new PF5 structure
    Which is MenuToggle->Select and not just Select as it was in PF4.
    """

    BUTTON_LOCATOR = './/button[contains(@class, "pf-v5-c-menu-toggle")]'
    DEFAULT_LOCATOR = './/div[contains(@class, "pf-v5-c-menu") and @data-ouia-component-type="PF5/Select"]'
    ROOT = f"{BUTTON_LOCATOR}/.."
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-v5-c-menu__list')]/li"
    ITEM_LOCATOR = "//*[contains(@class, 'pf-v5-c-menu__item') and .//*[contains(normalize-space(.), {})]]"


class ChangeHostsOwnerModal(PF5Modal):
    """
    This class represents the Change Hosts Owner modal,
    that is used to change the owner of one or more hosts.
    """

    OUIA_ID = "bulk-change-owner-modal"

    title = './/h1[@class="pf-v5-c-modal-box__title"]'
    close_btn = PF5OUIAButton("bulk-change-owner-modal-ModalBoxCloseButton")
    confirm_btn = PF5OUIAButton("bulk-change-owner-modal-add-button")
    cancel_btn = PF5OUIAButton("bulk-change-owner-modal-cancel-button")

    owner_select = MenuToggleSelect()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class BaseChangeOrgLocModal(PF5Modal):
    """
    Base class representing the modal for changing organization or location.
    """

    title = './/h1[@class="pf-v5-c-modal-box__title"]'

    menu_toggle = PF5Menu(locator='.//button[@class="pf-v5-c-menu-toggle"]')

    success_alert = PF5Alert(
        locator='.//div[contains(@class,"pf-v5-c-alert pf-m-success")]//following-sibling::h4[contains(@class, "-c-alert__title")]'
    )
    error_alert = PF5Alert(
        locator='.//div[contains(@class,"pf-v5-c-alert pf-m-danger")]//following-sibling::h4[contains(@class, "-c-alert__title")]'
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ChangeOrganizationModal(BaseChangeOrgLocModal):
    """
    This class represents 'Change organization' modal that is used to change organization
    for one or more hosts
    """

    OUIA_ID = "bulk-assign-taxonomy-modal"

    organization_menu = MenuToggleSelect()

    organization_fix_on_mismatch = PF5Radio(id="radio-fix-on-mismatch-organization")
    organization_fail_on_mismatch = PF5Radio(id="radio-fail-on-mismatch-organization")

    save_button = PF5OUIAButton("bulk-assign-organization-modal-add-button")
    cancel_button = PF5OUIAButton("bulk-assign-organization-modal-cancel-button")


class ChangeLocationModal(BaseChangeOrgLocModal):
    """
    This class represents 'Change location' modal that is used to change location
    for one or more hosts
    """

    OUIA_ID = "bulk-assign-location-modal"

    location_menu = MenuToggleSelect()

    location_fix_on_mismatch = PF5Radio(id="radio-fix-on-mismatch-location")
    location_fail_on_mismatch = PF5Radio(id="radio-fail-on-mismatch-location")

    save_button = PF5OUIAButton("bulk-assign-location-modal-add-button")
    cancel_button = PF5OUIAButton("bulk-assign-location-modal-cancel-button")
