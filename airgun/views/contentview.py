from widgetastic.widget import (
    Checkbox,
    ParametrizedView,
    Text,
    TextInput,
    View,
)

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatTab,
    SatTable,
    SatTabWithDropdown,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    EditableEntryCheckbox,
    PublishPromoteProgressBar,
    ReadOnlyEntry,
    Search,
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
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        description = EditableEntry(name='Description')
        composite = ReadOnlyEntry(name='Composite?')
        force_puppet = EditableEntryCheckbox(name='Force Puppet')

    @View.nested
    class versions(SatTab):
        searchbox = Search()
        resources = SatTable(
            locator='//table',
            column_widgets={
                'Version': Text('.//a'),
                'Status': PublishPromoteProgressBar(),
                'Actions': ActionsDropdown(
                    './div[contains(@class, "btn-group")]')
            },
        )

        def search(self, version_name):
            """Searches for content view version.

            Searchbox can't search by version name, only by id, that's why in
            case version name was passed, it's transformed into recognizable
            value before filling, for example::

                'Version 1.0' -> 'version = 1'
            """
            search_phrase = version_name
            if version_name.startswith('V') and '.' in version_name:
                search_phrase = 'version = {}'.format(
                    version_name.split()[1].split('.')[0])
            self.searchbox.search(search_phrase)
            return self.resources.read()

    @View.nested
    class yumrepo(SatTabWithDropdown):
        TAB_NAME = 'Yum Content'
        SUB_ITEM = 'Repositories'

        repos = View.nested(AddRemoveResourcesView)


class ContentViewVersionPublishView(BaseLoggedInView):
    version = Text('//div[@label="Version"]/div/span')
    description = TextInput(id='description')
    force_metadata_regeneration = Checkbox(id='forceMetadataRegeneration')
    save = Text('//button[contains(@ng-click, "handleSave()")]')
    cancel = Text('//button[contains(@ng-click, "handleCancel()")]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.save, exception=False) is not None


class ContentViewVersionPromoteView(BaseLoggedInView):
    lce = ParametrizedView.nested(LCESelectorGroup)
    description = TextInput(id='description')
    force_metadata_regeneration = Checkbox(id='forceMetadataRegeneration')
    promote = Text('//button[contains(@ng-click, "verifySelection()")]')
    cancel = Text(
        '//a[contains(@class, "btn")][@ui-sref="content-view.versions"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.save, exception=False) is not None
