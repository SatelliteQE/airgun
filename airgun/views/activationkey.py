from widgetastic.widget import Checkbox, Select, Text, TextInput

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import (
    ConfirmationDialog,
    EditableEntry,
    EditableEntrySelect,
    LCESelector,
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


class ActivationKeyDetailsView(BaseLoggedInView):

    name = TextInput(id='name')
    description = TextInput(id='description')
    unlimited_hosts = Checkbox(name='limit')
    max_hosts = TextInput(id='max_hosts')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")
    lce = LCESelector()
    content_view = Select(id='content_view_id')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ActivationKeyEditView(BaseLoggedInView):
    return_to_all = Text("//a[text()='Activation Keys']")
    name = EditableEntry(name='Name')
    description = EditableEntry(name='Description')
    host_limit = EditableEntry(name='Host Limit')
    service_level = EditableEntrySelect(name='Service Level')
    action_list = SelectActionList()
    dialog = ConfirmationDialog()
    lce = LCESelector()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None
