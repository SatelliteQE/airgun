from widgetastic.widget import ParametrizedView, Select, Text, TextInput, View

from airgun.views.common import (
    AddRemoveSubscriptionsView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ConfirmationDialog,
    EditableEntry,
    EditableEntrySelect,
    EditableLimitEntry,
    LimitInput,
    SelectActionList,
)


class ActivationKeyView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Activation Keys')]")
    new = Text("//button[contains(@href, '/activation_keys/new')]")
    edit = Text(
        "//td/a[contains(@ui-sref, 'info') and "
        "contains(@href, 'activation_keys')]"
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ActivationKeyCreateView(BaseLoggedInView):

    name = TextInput(id='name')
    hosts_limit = LimitInput()
    description = TextInput(id='description')
    lce = ParametrizedView.nested(LCESelectorGroup)
    content_view = Select(id='content_view_id')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ActivationKeyEditView(BaseLoggedInView):
    return_to_all = Text("//a[text()='Activation Keys']")
    name = EditableEntry(name='Name')
    description = EditableEntry(name='Description')
    hosts_limit = EditableLimitEntry(name='Host Limit')
    service_level = EditableEntrySelect(name='Service Level')
    lce = ParametrizedView.nested(LCESelectorGroup)
    action_list = SelectActionList()
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None

    @View.nested
    class subscriptions(SatTab):
        resources = View.nested(AddRemoveSubscriptionsView)
