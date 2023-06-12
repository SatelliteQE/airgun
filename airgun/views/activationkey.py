from widgetastic.widget import Checkbox
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Select
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import AddRemoveResourcesView
from airgun.views.common import AddRemoveSubscriptionsView
from airgun.views.common import BaseLoggedInView
from airgun.views.common import LCESelectorGroup
from airgun.views.common import SatTab
from airgun.views.common import SatTabWithDropdown
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import EditableEntrySelect
from airgun.widgets import EditableLimitEntry
from airgun.widgets import LimitInput


class ActivationKeysView(BaseLoggedInView, SearchableViewMixin):
    """View for the ActivationKeys page"""

    title = Text("//h2[contains(., 'Activation Keys')]")
    new = Text("//button[contains(@href, '/activation_keys/new')]")
    table = Table('.//table', column_widgets={'Name': Text('./a')})

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
        service_level = EditableEntrySelect(name='Service Level')
        lce = ParametrizedView.nested(LCESelectorGroup)
        content_view = EditableEntrySelect(name='Content View')

    @View.nested
    class subscriptions(SatTab):
        resources = View.nested(AddRemoveSubscriptionsView)

    @View.nested
    class repository_sets(SatTab):
        TAB_NAME = 'Repository Sets'
        repo_type = Select(locator='.//select[@id="repositoryTypes"]')
        table = Table(
            locator=".//table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Repository Name': Text('./td'),
                'Product Name': Text('./a'),
                'Repository path': Text('./td'),
                'Status': Text('./td'),
            },
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
