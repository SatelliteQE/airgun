from widgetastic.widget import (
    Checkbox,
    Text,
    TextInput,
    ParametrizedView,
    Select,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatTab,
    SearchableViewMixin,
    TaskDetailsView,
)
from airgun.views.job_invocation import JobInvocationCreateView
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableLimitEntry,
    RadioGroup,
    ReadOnlyEntry,
    SatTable,
    Search
)
from airgun.views.contenthost import UnEvenActionDropDown


class HostCollectionsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Host Collections')]")
    new = Text("//button[contains(@href, '/host_collections/new')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    unlimited_hosts = Checkbox(name='limit')
    max_hosts = TextInput(id='max_hosts')
    description = TextInput(id='description')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Host Collections'
                and self.breadcrumb.read() == 'New Host Collection'
        )


class HostCollectionEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Host Collections'
                and self.breadcrumb.read() != 'New Host Collection'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        description = EditableEntry(name='Description')
        content_hosts = ReadOnlyEntry(
            locator=(".//dt[contains(., 'Content Hosts')]/following-sibling"
                     "::dd/a[not(contains(@class, 'ng-hide'))][1]")
        )
        content_host_limit = EditableLimitEntry(name='Content Host Limit')
        # Package Installation, Removal, and Update
        manage_packages = Text(".//a[@ng-click='openPackagesModal()']")
        # Errata Installation
        install_errata = Text(".//a[@ng-click='openErrataModal()']")
        # Module Stream Installation, Removal, and Update
        manage_module_streams = Text(".//a[@ng-click='openModuleStreamsModal()']")
        # Change assigned Lifecycle Environment or Content View
        change_assigned_content = Text(
            ".//a[@ng-click='openEnvironmentModal()']")

    @View.nested
    class hosts(SatTab):
        TAB_NAME = 'Hosts'

        resources = View.nested(AddRemoveResourcesView)


class HostCollectionPackageContentRadioGroup(RadioGroup):
    """Handle an HTML non normalized Radio group according to the current
    architecture.
    Note: This is a temporary solution, a fix will be issued upstream,
        when the fix will be available downstream we should replace the
        implementation with RadioGroup.
    Example html representation::

        <div >
            <input type="radio" id="package" ...>
            <label>Package</label>
            <input type="radio" id="package_group" ...>
            <label>Package Group</label>
      """
    # a mapping between button name and the id, see the implementation in
    # HostsAssignOrganization and HostsAssignLocation hereafter.
    buttons_name_id_map = {
        'Package': 'package',
        'Package Group': 'package_group',
    }

    def get_input_by_name(self, name):
        input_id = self.buttons_name_id_map.get(name)
        if input_id:
            return self.browser.wait_for_element(
                ".//input[@id='{0}']".format(self.buttons_name_id_map[name])
            )
        return None

    @property
    def selected(self):
        """Return the name of the button that is currently selected."""
        for name in self.buttons_name_id_map.keys():
            btn = self.get_input_by_name(name)
            if btn and btn.get_attribute('checked') is not None:
                return name
        else:
            raise ValueError(
                "Whether no radio button is selected or proper attribute "
                "should be added to framework"
            )

    def select(self, name):
        """Select specific radio button in the group"""
        if self.selected != name:
            btn = self.get_input_by_name(name)
            if btn:
                btn.click()
                return True
        return False


class HostCollectionManagePackagesView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Update Packages')]")
    update_all = ActionsDropdown(
        "//span[contains(@class, 'input-group')]"
        "[button[contains(@ng-click, 'update all')]]"
    )
    content_type = HostCollectionPackageContentRadioGroup(
        "//div[@name='systemContentForm']/div")

    packages = TextInput(
        locator=("//input[@type='text' and "
                 "contains(@ng-model, 'content.content')]")
    )
    install = ActionsDropdown(
        "//span[contains(@class, 'input-group')]"
        "[button[contains(@ng-click, 'install')]]"
    )
    update = ActionsDropdown(
            "//span[contains(@class, 'input-group')]"
            "[button[contains(@ng-click, 'update') "
            "and not(contains(@ng-click, 'update all'))]]"
    )
    remove = ActionsDropdown(
        "//span[contains(@class, 'input-group')]"
        "[button[contains(@ng-click, 'remove')]]"
    )
    done = Text("//button[@ng-click='ok()']")

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    @View.nested
    class dialog(ConfirmationDialog):
        ROOT = ".//div[@class='inline-confirmation']"
        confirm_dialog = Text(locator=".//button[@type='submit']")
        cancel_dialog = Text(locator=".//button[@type='button']")

    def get_action_button(self, name):
        """Return an action button by it's name"""
        action_button = getattr(self, name)
        if not isinstance(action_button, ActionsDropdown):
            raise ValueError(
                'Action with name: "{0}" does not exists'.format(name))
        return action_button

    def apply_action(self, name, action_via='via Katello Agent'):
        """Apply an action by name using action via if indicated"""
        action_button = self.get_action_button(name)
        action_button.fill(action_via)
        if self.dialog.is_displayed:
            self.dialog.confirm()


class HostCollectionInstallErrataView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host Errata Management')]")
    search = TextInput(
        locator=".//input[@type='text' and @ng-model='errataFilter']")
    refresh = Text(locator=".//button[@ng-click='fetchErrata()']")
    install = ActionsDropdown(
            "//span[contains(@class, 'btn-group')]"
            "[button[contains(@class, 'btn') "
            "and contains(@ng-click, 'showConfirm')]]"
    )
    table = SatTable(
        ".//table",
        column_widgets={
            0: Checkbox(
                locator=".//input[@ng-model='erratum.selected']"),
            'Id': Text(locator="./a[@ng-click='transitionToErrata(erratum)']"),
        }
    )
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionManageModuleStreamsView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host Module Stream Management')]")
    search_box = Search()
    table = SatTable(
        locator='//table',
        column_widgets={
            'Name': Text('.//a'),
            'Actions': UnEvenActionDropDown(".//div[contains(@class, 'dropdown')]")
        },
    )

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def search(self, query):
        """search module stream based on name and stream version"""
        self.search_box.search(query)
        return self.table.read()


class HostCollectionChangeAssignedContentView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host Bulk Content')]")
    lce = ParametrizedView.nested(LCESelectorGroup)
    content_view = Select(
        locator=".//select[@ng-model='selected.contentView']")
    assign = Text(
        locator=".//form/button[contains(@ng-click, 'showConfirm')]")

    @View.nested
    class dialog(ConfirmationDialog):
        ROOT = ".//div[@ng-show='showConfirm']"
        confirm_dialog = Text(
            ".//button[contains(@ng-click, 'performAction')]"
        )
        cancel_dialog = Text(
            ".//button[contains(@ng-click, 'showConfirm')"
            " and not(contains(@ng-click, 'performAction'))]"
        )

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionActionTaskDetailsView(TaskDetailsView):
    title = Text("//h4[contains(., 'Task Details')]")
    breadcrumb = None

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionActionRemoteExecutionJobCreate(JobInvocationCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Remote Executions'
            and self.breadcrumb.read() == 'Job invocation'
        )
