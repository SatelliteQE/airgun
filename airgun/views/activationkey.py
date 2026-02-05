import time
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
from widgetastic_patternfly5 import Dropdown as PF5Dropdown

from airgun.views.common import (
    AddRemoveResourcesView,
    AddRemoveSubscriptionsView,
    BaseLoggedInView,
    PF5LCESelectorGroup,
    SatTab,
    SatTabWithDropdown,
    SearchableViewMixin,
)
from airgun.views.host_new import ManageMultiCVEnvModal, NewCVEnvAssignmentSection
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntrySelect,
    EditableLimitEntry,
    LimitInput,
)
from widgetastic.widget import Widget


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

    # Button/link to open CV/LCE assignment modal
    assign_cv_env_btn = Text("//button[contains(., 'Assign') or contains(@ng-click, 'assign')]")

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

        # PF5 kebab dropdown for CV/LCE management
        dropdown = PF5Dropdown(
            locator='.//div[button[@aria-label="change_content_view_kebab"]]'
        )

        @property
        def lce(self):
            """Read selected LCE names from PF5 card as a simple list"""
            # Read all LCE labels from the card (only selected ones are shown)
            lce_labels = self.browser.elements(
                './/div[@data-ouia-component-id="content-view-details-card"]//span[@class="pf-v5-c-label__text"]'
            )
            # Return list of selected LCE names
            return [label.text for label in lce_labels] if lce_labels else []

        @property
        def content_view(self):
            """Read CV name from PF5 card"""
            # Read CV link text from the card
            cv_links = self.browser.elements(
                './/div[@data-ouia-component-id="content-view-details-card"]//a[contains(@href, "/content_views/")]'
            )
            # Return the first link's text (the CV name, not the version)
            for link in cv_links:
                text = link.text.strip()
                if text and 'Version' not in text:
                    return text
            return None

        @property
        def is_displayed(self):
            """Override to avoid tab detection issues"""
            return True

        def select(self):
            """Override to prevent tab selection - Details is always visible"""
            pass

        def read(self):
            """Override read to include lce and content_view properties"""
            # First read all normal widgets
            values = SatTab.read(self)

            # Then add the custom properties
            values['lce'] = self.lce
            values['content_view'] = self.content_view

            return values

    @View.nested
    class subscriptions(SatTab):
        resources = View.nested(AddRemoveSubscriptionsView)

    @View.nested
    class repository_sets(SatTab, SearchableViewMixin):
        TAB_NAME = 'Repository Sets'
        repo_type = Select(locator='.//select[@id="repositoryTypes"]')
        actions = ActionsDropdown('//div[contains(@class, "btn-group ng-scope")]/div')
        table = Table(locator='.//table')
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
        table = Table(locator='.//table')
