import re

from widgetastic.widget import Checkbox
from widgetastic.widget import GenericLocatorWidget
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Button

from airgun.views.common import AddRemoveResourcesView
from airgun.views.common import AddRemoveSubscriptionsView
from airgun.views.common import BaseLoggedInView
from airgun.views.common import LCESelectorGroup
from airgun.views.common import SatTab
from airgun.views.common import SatTable
from airgun.views.common import SatTabWithDropdown
from airgun.views.common import SearchableViewMixin
from airgun.views.common import TaskDetailsView
from airgun.widgets import ActionDropdownWithCheckbox
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import EditableEntryCheckbox
from airgun.widgets import EditableEntryMultiCheckbox
from airgun.widgets import EditableEntrySelect
from airgun.widgets import Pagination
from airgun.widgets import ReadOnlyEntry
from airgun.widgets import Search


class StatusIcon(GenericLocatorWidget):
    """Small icon indicating subscription or katello-agent status. Can be
    colored in either green, yellow or red.

    Example html representation::

        <span
         ng-class="table.getHostStatusIcon(host.subscription_global_status)"
         class="red host-status pficon pficon-error-circle-o status-error">
        </span>

    Locator example::

        //span[contains(@ng-class, 'host.subscription_global_status')]
        //i[contains(@ng-class, 'host.subscription_global_status')]
    """

    def __init__(self, parent, locator=None, logger=None):
        """Provide default locator value if it wasn't passed"""
        if not locator:
            locator = ".//span[contains(@ng-class, 'host.subscription_global_status')]"
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def color(self):
        """Returns string representing icon color: 'red', 'yellow', 'green' or
        'unknown'.
        """
        colors = {
            'rgba(204, 0, 0, 1)': 'red',
            'rgba(236, 122, 8, 1)': 'yellow',
            'rgba(63, 156, 53, 1)': 'green',
        }
        return colors.get(
            self.browser.element(self, parent=self.parent).value_of_css_property('color'),
            'unknown',
        )

    def read(self):
        """Returns current icon color"""
        return self.color


class InstallableUpdatesCellView(View):
    """Installable Updates Table Cell View for content host view Table"""

    ROOT = '.'

    @View.nested
    class errata(View):
        ROOT = "./a[contains(@ui-sref, 'errata')]"

        security = Text(".//span[contains(@ng-class, 'errataCounts.security')]")
        bug_fix = Text(".//span[contains(@ng-class, 'errataCounts.bugfix')]")
        enhancement = Text(".//span[contains(@ng-class, 'errataCounts.enhancement')]")


class ContentHostsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Content Hosts')]")
    export = Text(".//a[contains(@class, 'btn')][contains(@href, 'content_hosts.csv')]")
    register = Text(".//button[@ui-sref='content-hosts.register']")
    actions = ActionsDropdown(".//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()
    select_all = Checkbox(locator="//input[@ng-model='selection.allSelected']")
    table = SatTable(
        './/table',
        column_widgets={
            0: Checkbox(locator="./input[@type='checkbox']"),
            'Name': Text('.//a'),
            'Subscription Status': StatusIcon(),
            'Installable Updates': InstallableUpdatesCellView(),
        },
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ContentHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    unregister = Text(".//button[@ng-click='openModal()']")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Hosts'
            and len(self.breadcrumb.locations) > 1
        )

    @View.nested
    class details(SatTab):
        # Basic information
        name = EditableEntry(name='Name')
        uuid = ReadOnlyEntry(name='Subscription UUID')
        bios_uuid = ReadOnlyEntry(name='BIOS UUID')
        description = EditableEntry(name='Description')
        type = ReadOnlyEntry(name='Type')
        katello_agent = ReadOnlyEntry(name='Katello Agent')
        virtual_guests = ReadOnlyEntry(name='Virtual Guests')
        registered_through = ReadOnlyEntry(name='Registered Through')
        # Subscriptions
        subscription_status = ReadOnlyEntry(name='Subscription Status')
        details = ReadOnlyEntry(name='Details')
        auto_attach = EditableEntryCheckbox(name='Auto-Attach')
        # System Purpose
        system_purpose_status = ReadOnlyEntry(name='System Purpose Status')
        service_level = EditableEntrySelect(name='Service Level (SLA)')
        usage_type = EditableEntrySelect(name='Usage Type')
        role = EditableEntrySelect(name='Role')
        addons = EditableEntryMultiCheckbox(name='Add ons')
        # Content Host Properties
        os = ReadOnlyEntry(
            locator=".//dt[.='OS']/following-sibling::dd[not(contains(@class, 'ng-hide'))]"
        )
        architecture = ReadOnlyEntry(name='Architecture')
        number_of_cpus = ReadOnlyEntry(name='Number of CPUs')
        sockets = ReadOnlyEntry(name='Sockets')
        cores_per_socket = ReadOnlyEntry(name='Cores per Socket')
        ram = ReadOnlyEntry(name='RAM (GB)')
        virtual_guest = ReadOnlyEntry(name='Virtual Guest')
        # Installable Errata
        security = ReadOnlyEntry(name='Security')
        bug_fix = ReadOnlyEntry(name='Bug Fix')
        enhancement = ReadOnlyEntry(name='Enhancement')
        # Content Host Content
        release_version = EditableEntrySelect(name='Release Version')
        content_view = EditableEntrySelect(name='Content View')
        lce = ParametrizedView.nested(LCESelectorGroup)
        # Content Host Status
        registered = ReadOnlyEntry(name='Registered')
        registered_by = ReadOnlyEntry(name='Registered By')
        last_checkin = ReadOnlyEntry(name='Last Checkin')

    @View.nested
    class provisioning_details(SatTab):
        TAB_NAME = 'Provisioning Details'
        name = ReadOnlyEntry(name='Name')
        status = ReadOnlyEntry(name='Status')
        operating_system = ReadOnlyEntry(name='Operating System')
        puppet_environment = ReadOnlyEntry(name='Puppet Environment')
        last_puppet_report = ReadOnlyEntry(name='Last Puppet Report')
        model = ReadOnlyEntry(name='Model')
        host_group = ReadOnlyEntry(name='Host Group')

    @View.nested
    class subscriptions(SatTab):
        SUB_ITEM = 'Subscriptions'

        status = ReadOnlyEntry(name='Status')
        auto_attach = EditableEntryCheckbox(name='Auto-Attach')
        run_auto_attach = Text(".//a[@ng-click='autoAttachSubscriptions()']")
        service_level = EditableEntrySelect(name='Service Level')

        resources = View.nested(AddRemoveSubscriptionsView)

    @View.nested
    class host_collections(SatTab):
        TAB_NAME = 'Host Collections'

        resources = View.nested(AddRemoveResourcesView)

    @View.nested
    class packages_actions(SatTabWithDropdown):
        TAB_NAME = 'Packages'
        SUB_ITEM = 'Actions'

        action_type = Select(name='remote_action')
        name = TextInput(locator='.//input[@ng-model="packageAction.term"]')
        perform = Button('Perform')
        update_all_packages = Button('Update All Packages')

    @View.nested
    class packages_installed(SatTabWithDropdown, SearchableViewMixin):
        TAB_NAME = 'Packages'
        SUB_ITEM = 'Installed'

        remove_selected = Button('Remove Selected')
        table = SatTable(
            './/table', column_widgets={0: Checkbox(locator="./input[@type='checkbox']")}
        )

    @View.nested
    class packages_applicable(SatTabWithDropdown, SearchableViewMixin):
        TAB_NAME = 'Packages'
        SUB_ITEM = 'Applicable'

        upgrade_selected = ActionsDropdown(".//span[contains(@class, 'btn-group')]")
        update_all_packages = Button('Update All Packages')
        table = SatTable(
            './/table', column_widgets={0: Checkbox(locator="./input[@type='checkbox']")}
        )

    @View.nested
    class errata(SatTab):
        lce_filter = Select(locator='.//select[@ng-model="selectedErrataOption"]')
        searchbox = Search()
        apply_selected = ActionsDropdown(".//span[contains(@class, 'btn-group dropdown')]")
        recalculate = Button('Recalculate')
        table = SatTable(
            './/table',
            column_widgets={
                0: Checkbox(locator="./input[@type='checkbox']"),
                'Id': Text('./a'),
            },
        )
        select_all = Checkbox(locator=".//input[@type='checkbox'][@ng-change='allSelected()']")
        pagination = Pagination()

        def search(self, query, lce=None):
            """Apply available filters before proceeding with searching and
            automatically set proper search mask if errata id instead of errata
            title was passed.

            :param str query: search query to type into search field. Both
                errata id (RHEA-2012:0055) and errata title (Sea_Erratum) are
                supported.
            :param str optional lce: filter by lifecycle environment
            :return: list of dicts representing table rows
            :rtype: list
            """
            if lce is not None:
                self.lce_filter.fill(lce)

            if re.search(r'\w{4}-\d{4}:\d{4}', query):
                query = f'id = {query}'
            self.searchbox.search(query)

            return self.table.read()

    @View.nested
    class module_streams(SatTab, SearchableViewMixin):
        TAB_NAME = 'Module Streams'
        status_filter = Select(locator='.//select[@ng-model="nutupaneParams.status"]')
        table = SatTable(
            locator='//table',
            column_widgets={
                'Name': Text('.//a'),
                'Actions': ActionDropdownWithCheckbox(".//div[contains(@class, 'dropdown')]"),
            },
        )

        def search(self, query, status='All'):
            """Searches for Module Streams. Apply available filters before
            proceeding with searching. By default 'All' is passed

            :param str query: search query to type into search field.
            :param str optional status: filter by status of module stream on host
            :return: list of dicts representing table rows
            :rtype: list
            """
            if status is not None:
                self.status_filter.fill(status)
            self.searchbox.search(query)
            return self.table.read()

    @View.nested
    class repository_sets(SatTab, SearchableViewMixin):
        TAB_NAME = 'Repository Sets'

        show_all = Checkbox(locator=".//input[contains(@ng-model, 'contentAccessModeAll')]")
        limit_to_lce = Checkbox(locator=".//input[contains(@ng-model, 'contentAccessModeEnv')]")
        actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")

        table = SatTable(
            './/table',
            column_widgets={
                0: Checkbox(locator="./input[@type='checkbox']"),
                'Product Name': Text('./a'),
            },
        )

        def read(self):
            """Sometimes no checkboxes are checked off by default, selecting
            "Show All" in such case.
            """
            if self.show_all.read() is False and self.limit_to_lce.read() is False:
                self.show_all.fill(True)
            return super().read()


class ContentHostTaskDetailsView(TaskDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Hosts'
            and len(self.breadcrumb.locations) > 2
        )


class SyspurposeBulkActionView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host System Purpose')]")
    service_level = Select(id='selectedServiceLevels')
    role = Select(id='selectedRoles')
    usage_type = Select(id='selectedUsages')
    assign = Text(".//span[normalize-space(.)='Assign']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ErrataDetailsView(BaseLoggedInView):

    breadcrumb = BreadCrumb()
    advisory = Text("//h3")
    type = ReadOnlyEntry(name='Type')
    title = ReadOnlyEntry(name='Title')
    issued = ReadOnlyEntry(name='Issued')
    updated = ReadOnlyEntry(name='Updated')
    description = ReadOnlyEntry(name='Description')
    last_updated_on = ReadOnlyEntry(name='Last Updated On')
    reboot_suggested = ReadOnlyEntry(name='Reboot Suggested')
    packages = ReadOnlyEntry(name='Packages')
    module_streams = ReadOnlyEntry(name='Module Streams')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[1] == 'Errata'
            and len(self.breadcrumb.locations) > 3
        )
