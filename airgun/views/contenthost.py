import re

from widgetastic.widget import (
    Checkbox,
    ParametrizedView,
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import (
    AddRemoveResourcesView,
    AddRemoveSubscriptionsView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatTab,
    SatTabWithDropdown,
    SatTable,
    SearchableViewMixin,
    TaskDetailsView,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntryCheckbox,
    EditableEntrySelect,
    ReadOnlyEntry,
    Search,
)


class ContentHostsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Content Hosts')]")
    export = Text(
        ".//a[contains(@class, 'btn')][contains(@href, 'content_hosts.csv')]")
    register = Text(".//button[@ui-sref='content-hosts.register']")
    actions = ActionsDropdown(".//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()
    table = SatTable(
        './/table',
        column_widgets={
            0: Checkbox(locator="./input[@type='checkbox']"),
            'Name': Text('./a'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ContentHostDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    unregister = Text(".//button[@ng-click='openModal()']")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Hosts'
            and len(self.breadcrumb.locations) > 1
        )

    @View.nested
    class details(SatTab):
        # Basic information
        name = EditableEntry(name='Name')
        uuid = ReadOnlyEntry(name='UUID')
        description = EditableEntry(name='Description')
        type = ReadOnlyEntry(name='Type')
        katello_agent = ReadOnlyEntry(name='Katello Agent')
        virtual_guests = ReadOnlyEntry(name='Virtual Guests')
        registered_through = ReadOnlyEntry(name='Registered Through')
        # Subscriptions
        subscription_status = ReadOnlyEntry(name='Subscription Status')
        details = ReadOnlyEntry(name='Details')
        auto_attach = EditableEntryCheckbox(name='Auto-Attach')
        service_level = EditableEntrySelect(name='Service Level')
        # Content Host Properties
        os = ReadOnlyEntry(name='OS')
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
    class subscriptions(SatTabWithDropdown):
        SUB_ITEM = 'Subscriptions'

        status = ReadOnlyEntry(name='Status')
        auto_attach = EditableEntryCheckbox(name='Auto-Attach')
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
            './/table',
            column_widgets={0: Checkbox(locator="./input[@type='checkbox']")}
        )

    @View.nested
    class packages_applicable(SatTabWithDropdown, SearchableViewMixin):
        TAB_NAME = 'Packages'
        SUB_ITEM = 'Applicable'

        upgrade_selected = ActionsDropdown(
            ".//span[contains(@class, 'btn-group')]")
        update_all_packages = Button('Update All Packages')
        table = SatTable(
            './/table',
            column_widgets={0: Checkbox(locator="./input[@type='checkbox']")}
        )

    @View.nested
    class errata(SatTab):
        lce_filter = Select(
            locator='.//select[@ng-model="selectedErrataOption"]')
        searchbox = Search()
        apply_selected = ActionsDropdown(
            ".//span[contains(@class, 'btn-group')]")
        recalculate = Button('Recalculate')
        table = SatTable(
            './/table',
            column_widgets={
                0: Checkbox(locator="./input[@type='checkbox']"),
                'Id': Text('./a'),

            }
        )

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
                query = 'id = {}'.format(query)
            self.searchbox.search(query)

            return self.table.read()

    @View.nested
    class repository_sets(SatTab, SearchableViewMixin):
        TAB_NAME = 'Repository Sets'

        show_all = Checkbox(
            locator=".//input[contains(@ng-model, 'contentAccessModeAll')]")
        limit_to_lce = Checkbox(
            locator=".//input[contains(@ng-model, 'contentAccessModeEnv')]")
        actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")

        table = SatTable(
            './/table',
            column_widgets={
                0: Checkbox(locator="./input[@type='checkbox']"),
                'Product Name': Text('./a'),
            }
        )

        def read(self):
            """Sometimes no checkboxes are checked off by default, selecting
            "Show All" in such case.
            """
            if (
                    self.show_all.read() is False
                    and self.limit_to_lce.read() is False):
                self.show_all.fill(True)
            return super().read()


class ContentHostTaskDetailsView(TaskDetailsView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Hosts'
                and len(self.breadcrumb.locations) > 2
        )
