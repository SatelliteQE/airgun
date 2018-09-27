from widgetastic.widget import (
    Checkbox,
    ParametrizedView,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    LCESelectorGroup,
    SatSecondaryTab,
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
    SatSelect,
    Search,
)


class ContentViewTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Content Views')]")
    new = Text("//a[contains(@href, '/content_views/new')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ContentViewCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    composite_view = Checkbox(id='composite')
    auto_publish = Checkbox(id='auto_publish')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() == 'New Content View'
        )


class ContentViewCopyView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    new_name = TextInput(id='copy_name')
    create = Text(".//button[@type='submit']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and len(self.breadcrumb.locations) == 3
                and self.breadcrumb.read() == 'Copy'
        )


class ContentViewRemoveView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    conflicts = Text("//div[@ng-show='conflictingVersions.length > 0']")
    table = SatTable('.//table')
    remove = Text(".//button[@ng-click='delete()']")
    cancel = Text(
        ".//a[contains(@class, 'btn')][@ui-sref='content-view.versions']")

    @property
    def conflicts_present(self):
        return 'ng-hide' not in self.browser.classes(self.conflicts)

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and len(self.breadcrumb.locations) == 3
                and self.breadcrumb.read() == 'Deletion'
                and (self.conflicts_present or self.remove.is_displayed)
        )


class ContentViewEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    publish = Text("//button[contains(., 'Publish New Version')]")
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() != 'New Content View'
        )

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
        table = SatTable(
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
            return self.table.read()

    @View.nested
    class content_views(SatTab):
        TAB_NAME = 'Content Views'

        resources = View.nested(AddRemoveResourcesView)

    @View.nested
    class repositories(SatTabWithDropdown):
        TAB_NAME = 'Yum Content'
        SUB_ITEM = 'Repositories'

        resources = View.nested(AddRemoveResourcesView)

    @View.nested
    class filters(SatTabWithDropdown, SearchableViewMixin):
        TAB_NAME = 'Yum Content'
        SUB_ITEM = 'Filters'

        new_filter = Text(".//button[@ui-sref='content-view.yum.filters.new']")
        remove_selected = Text(".//button[@ng-click='removeFilters()']")

        table = SatTable(
            locator='//table',
            column_widgets={
                0: Checkbox(locator=".//input[@type='checkbox']"),
                'Name': Text('./a'),
            },
        )

    @View.nested
    class puppet_modules(SatTab):
        TAB_NAME = 'Puppet Modules'

        add_new_module = Text(
            './/button[@ui-sref="content-view.puppet-modules.names"]')
        table = SatTable('.//table')


class AddNewPuppetModuleView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()
    table = SatTable(
        locator='.//table',
        column_widgets={
            'Actions': Text('./button[@ng-click="selectVersion(item.name)"]')
        }
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() == 'Add Puppet Module'
        )


class SelectPuppetModuleVersionView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()
    table = SatTable(
        locator='.//table',
        column_widgets={
            'Actions': Text('./button[@ng-click="selectVersion(item)"]')
        }
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() == 'Version for Module:'
        )


class ContentViewVersionPublishView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    version = Text('//div[@label="Version"]/div/span')
    description = TextInput(id='description')
    force_metadata_regeneration = Checkbox(id='forceMetadataRegeneration')
    save = Text('//button[contains(@ng-click, "handleSave()")]')
    cancel = Text('//button[contains(@ng-click, "handleCancel()")]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() == 'Publish'
        )


class ContentViewVersionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and len(self.breadcrumb.locations) > 3
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.locations[2] == 'Versions'
        )

    @View.nested
    class yum_repositories(SatSecondaryTab, SearchableViewMixin):
        TAB_NAME = 'Yum Repositories'
        table = SatTable('.//table')

    @View.nested
    class rpm_packages(SatSecondaryTab):
        TAB_NAME = 'rpm Packages'
        repo_filter = SatSelect(".//select[@ng-model='repository']")
        searchbox = Search()
        table = SatTable(".//table")

        def search(self, query, repo=None):
            """Apply available filters before proceeding with searching.

            :param str query: search query to type into search field.
            :param str optional repo: filter by repository name
            :return: list of dicts representing table rows
            :rtype: list
            """
            if repo:
                self.repo_filter.fill(repo)
            self.searchbox.search(query)
            return self.table.read()

    @View.nested
    class errata(SatSecondaryTab, SearchableViewMixin):
        table = SatTable(
            locator='.//table',
            column_widgets={'Title': Text('./a')}
        )

    @View.nested
    class details(SatSecondaryTab):
        description = ReadOnlyEntry(name='Description')
        environments = ReadOnlyEntry(name='Environments')


class ContentViewVersionPromoteView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    lce = ParametrizedView.nested(LCESelectorGroup)
    description = TextInput(id='description')
    force_metadata_regeneration = Checkbox(id='forceMetadataRegeneration')
    promote = Text('//button[contains(@ng-click, "verifySelection()")]')
    cancel = Text(
        '//a[contains(@class, "btn")][@ui-sref="content-view.versions"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() == 'Promotion'
        )


class ContentViewVersionRemoveView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    table = SatTable(
        locator='.//table',
        column_widgets={
            0: Checkbox(locator="./input[@type='checkbox']"),
        }
    )
    completely = Checkbox(
        locator=".//input[@ng-model='deleteOptions.deleteArchive']")
    next = Text(".//button[@ng-click='processSelection()']")
    cancel = Text(".//button[normalize-space(.)='Cancel']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and len(self.breadcrumb.locations) == 3
                and self.breadcrumb.read() == 'Deletion'
                and self.next.is_displayed
        )


class ContentViewVersionRemoveConfirmationView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    cancel = Text(".//button[normalize-space(.)='Cancel']")
    back = Text(".//button[@ng-click='transitionBack()']")
    confirm_remove = Text(".//button[@ng-click='performDeletion()']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Content Views'
                and len(self.breadcrumb.locations) == 3
                and self.breadcrumb.read() == 'Deletion'
                and self.confirm_remove.is_displayed
        )
