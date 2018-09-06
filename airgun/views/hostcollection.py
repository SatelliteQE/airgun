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
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableLimitEntry,
    RadioGroup,
    SatTable,
)


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
        content_host_limit = EditableLimitEntry(name='Content Host Limit')
        # Package Installation, Removal, and Update
        manage_packages = Text(".//li[@bst-feature-flag='remote_actions']"
                               "/a[@ng-click='openPackagesModal()']")
        # Errata Installation
        install_errata = Text(".//li[@bst-feature-flag='remote_actions']"
                              "/a[@ng-click='openErrataModal()']")
        # Change assigned Lifecycle Environment or Content View
        change_assigned_content = Text(
            ".//li[@bst-feature-flag='lifecycle_environments']"
            "/a[@ng-click='openEnvironmentModal()']"
        )

        @View.nested
        class content_hosts(View):
            ROOT = ("//dt[normalize-space(.)='Content Hosts']"
                    "/following-sibling::dd[1]")
            add_hosts = Text(
                "./a[contains(@ui-sref, 'host-collection.hosts.add')]")
            list_hosts = Text(
                "./a[contains(@ui-sref, 'host-collection.hosts.list')]")

            def read(self):
                if self.add_hosts.is_displayed:
                    return self.add_hosts.read()
                else:
                    return self.list_hosts.read()

            def click(self):
                if self.add_hosts.is_displayed:
                    # This click should open hosts>resources>AddTab
                    return self.add_hosts.click()
                else:
                    # This click should open hosts>resources>ListRemoveTab
                    return self.list_hosts.click()

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

    def read(self):
        """Wrap method according to architecture"""
        return self.selected

    def fill(self, name):
        """Wrap method according to architecture"""
        return self.select(name)


class HostCollectionManagePackagesView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Update Packages')]")
    update_all = ActionsDropdown(
        "//button[contains(@class, 'btn')][contains(@ng-click, 'update all')]"
        "/ancestor::span[contains(@class, 'input-group')]"
    )
    content_type = HostCollectionPackageContentRadioGroup(
        "//div[@name='systemContentForm']/div")

    packages = TextInput(
        locator=("//input[@type='text' and "
                 "contains(@ng-model, 'content.content')]")
    )
    install = ActionsDropdown(
        "//button[contains(@class, 'btn')][contains(@ng-click, 'install')]"
        "/ancestor::span[contains(@class, 'input-group')]"
    )
    update = ActionsDropdown(
        "//button[contains(@class, 'btn') and contains(@ng-click, 'update')"
        " and not(contains(@ng-click, 'update all'))]"
        "/ancestor::span[contains(@class, 'input-group')]"
    )
    remove = ActionsDropdown(
        "//button[contains(@class, 'btn')][contains(@ng-click, 'remove')]"
        "/ancestor::span[contains(@class, 'input-group')]"
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
        confirm_dialog = Text(
            locator=("//div[@ng-show='content.confirm']"
                     "//button[@type='submit']")
        )
        cancel_dialog = Text(
            locator=("//div[@ng-show='content.confirm']"
                     "//button[@type='button']"
                     "[@ng-click='content.confirm = false']")
        )

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
        if action_via:
            action_button.select(action_via)
        else:
            action_button.button.click()
            self.dialog.confirm()


class HostCollectionInstallErrataView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host Errata Management')]")

    search = TextInput(
        locator=".//input[@type='text'][@ng-model='errataFilter']")
    refresh = Text(locator=".//button[@ng-click='fetchErrata()']")
    install = ActionsDropdown(
            "//button[contains(@class, 'btn')]"
            "[contains(@ng-click, 'showConfirm')]"
            "/ancestor::span[contains(@class, 'btn-group')]"
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


class HostCollectionChangeAssignedContentView(BaseLoggedInView):
    title = Text("//h4[contains(., 'Content Host Bulk Content')]")

    lce = ParametrizedView.nested(LCESelectorGroup)
    content_view = Select(
        locator=".//select[@ng-model='selected.contentView']")
    assign = Text(
        locator=".//form//button[contains(@ng-click, 'showConfirm')]")

    @View.nested
    class dialog(ConfirmationDialog):
        confirm_dialog = Text(
            ".//div[@ng-show='showConfirm']"
            "//button[contains(@ng-click, 'performAction')]"
        )
        cancel_dialog = Text(
            ".//div[@ng-show='showConfirm']"
            "//button[contains(@ng-click, 'showConfirm')"
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
