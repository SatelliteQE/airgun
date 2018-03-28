from widgetastic.widget import Checkbox, Text, TextInput, View

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ConfirmationDialog,
    EditableEntry,
    EditableEntryCheckbox,
    ReadOnlyEntry,
    SelectActionList,
)


class ContentViewTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Content Views')]")
    new = Text("//a[contains(@href, '/content_views/new')]")
    edit = Text(
        "//td/a[contains(@ui-sref, 'content-view') and "
        "contains(@href, 'content_views')]"
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ContentViewCreateView(BaseLoggedInView):
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    composite_view = Checkbox(id='composite')
    auto_publish = Checkbox(id='auto_publish')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ContentViewEditView(BaseLoggedInView):
    return_to_all = Text("//a[text()='Content Views']")
    publish = Text("//button[contains(., 'Publish New Version')]")
    action_list = SelectActionList()
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None

    @View.nested
    class Details(SatTab):
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        description = EditableEntry(name='Description')
        composite = ReadOnlyEntry(name='Composite?')
        force_puppet = EditableEntryCheckbox(name='Force Puppet')
