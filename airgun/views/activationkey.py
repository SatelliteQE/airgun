from widgetastic.widget import (
    Checkbox,
    Select,
    Table,
    Text,
    TextInput,
    View,
    Widget,
)
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly5 import Dropdown as PF5Dropdown

from airgun.views.common import (
    AddRemoveResourcesView,
    AddRemoveSubscriptionsView,
    BaseLoggedInView,
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


class LCEListWidget(Widget):
    """Widget to read LCE names from PF5 content-view-details-card as a list"""

    ROOT = './/div[@data-ouia-component-id="content-view-details-card"]'

    def read(self):
        """Read all LCE labels from the card"""
        lce_labels = self.browser.elements('.//span[@class="pf-v5-c-label__text"]', parent=self)
        return [label.text for label in lce_labels] if lce_labels else []


class ContentViewWidget(Widget):
    """Widget to read Content View name from PF5 content-view-details-card"""

    ROOT = './/div[@data-ouia-component-id="content-view-details-card"]'

    def read(self):
        """Read CV name from the card.

        Note: For long CV names, the UI truncates them with "..." so we strip that suffix.
        The returned value may be a truncated prefix of the actual CV name.
        """
        cv_links = self.browser.elements(
            './/a[contains(@href, "/content_views/") and not(contains(@href, "/versions/"))]',
            parent=self,
        )
        # Return the first link's text (the CV name, not the version)
        for link in cv_links:
            text = link.text.strip()
            if text and 'Version' not in text:
                # Strip "..." suffix if present (indicates truncation)
                if text.endswith('...'):
                    text = text[:-3]  # Remove the last 3 characters ("...")
                return text
        return None


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
        dropdown = PF5Dropdown(locator='.//div[button[@aria-label="change_content_view_kebab"]]')

        # Custom widgets to read LCE and CV from PF5 card
        lce = LCEListWidget()
        content_view = ContentViewWidget()

        @property
        def is_displayed(self):
            """Override to avoid tab detection issues"""
            return True

        def select(self):
            """Override to prevent tab selection - Details is always visible"""
            pass

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
