from widgetastic.widget import Checkbox, Text, View
from widgetastic_patternfly4 import Button, Dropdown, Menu, Radio
from widgetastic_patternfly4.ouia import (
    PatternflyTable,
)

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixinPF4,
)
from airgun.views.host_new import ManageColumnsView, PF4CheckboxTreeView


class AllHostsMenu(Menu):
    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-menu-toggle')]"
    ROOT = f"{BUTTON_LOCATOR}/.."


class AllHostsTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Hosts']")
    select_all = Checkbox(
        locator='.//input[@data-ouia-component-id="select-all-checkbox-dropdown-toggle-checkbox"]'
    )
    bulk_actions = AllHostsMenu()
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
