from widgetastic.widget import (
    Checkbox,
    ParametrizedView,
    Select,
    Table,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    AddRemoveResourcesView,
    AddRemoveSubscriptionsView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatTab,
    SatTabWithDropdown,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntrySelect,
    EditableLimitEntry,
    LimitInput,
)


class ActivationKeysView(BaseLoggedInView, SearchableViewMixin):
    """View for the ActivationKeys page"""

    title = Text("//h2[contains(., 'Activation Keys')]")
    new = Text("//button[contains(@href, '/activation_keys/new')]")
    table = Table('.//table', column_widgets={'Name': Text('.//a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ActivationKeyCreateView(BaseLoggedInView):
    """View for the ActivationKeys Create page"""

    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    hosts_limit = LimitInput()
    description = TextInput(id='description')
    lce = ParametrizedView.nested(LCESelectorGroup)
    content_view = Select(id='content_view_id')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Activation Keys'
            and self.breadcrumb.read() == 'New Activation Key'
        )


class ActivationKeyEditView(BaseLoggedInView):
    """View for the ActivationKeys Edit page"""

    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Activation Keys'
            and self.breadcrumb.read() != 'New Activation Key'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        description = EditableEntry(name='Description')
        hosts_limit = EditableLimitEntry(name='Host Limit')
        host_limit_edit_btn = Text(
            locator='//dd[@bst-edit-custom="activationKey.max_hosts"]//div[@ng-click="edit()"]'
        )
        unlimited_content_host_checkbox = Checkbox(
            locator='//input[@ng-model="activationKey.unlimited_hosts"]'
        )
        host_limit_input = TextInput(locator='//input[@ng-model="activationKey.max_hosts"]')
        host_limit_save_btn = Text(
            locator='//dd[contains(@bst-edit-custom, "activationKey.max_hosts")]//button[@ng-click="save()"]'
        )
        host_limit_cancel_btn = Text(
            locator='//dd[contains(@bst-edit-custom, "activationKey.max_hosts")]//button[@ng-click="cancel()"]'
        )

        service_level = EditableEntrySelect(name='Service Level')
        lce = ParametrizedView.nested(LCESelectorGroup)
        content_view = EditableEntrySelect(name='Content View')

    @View.nested
    class subscriptions(SatTab):
        resources = View.nested(AddRemoveSubscriptionsView)

    @View.nested
    class repository_sets(SatTab, SearchableViewMixin):
        TAB_NAME = 'Repository Sets'
        repo_type = Select(locator='.//select[@id="repositoryTypes"]')
        actions = ActionsDropdown('//div[contains(@class, "btn-group ng-scope")]/div')
        table = Table(locator=".//table")
        repository_name = Text(
            locator='//table[@class="table table-bordered table-striped"]/tbody/tr//td[2]'
        )
        check_box = Checkbox(
            locator='//table[@class="table table-bordered table-striped"]/tbody/tr//td[1]'
        )

    @View.nested
    class host_collections(SatTab):
        TAB_NAME = 'Host Collections'
        resources = View.nested(AddRemoveResourcesView)

    @View.nested
    class content_hosts(SatTabWithDropdown):
        TAB_NAME = 'Associations'
        SUB_ITEM = 'Content Hosts'
        table = Table(locator=".//table")
