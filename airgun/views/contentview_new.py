from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb, Tab
from widgetastic_patternfly4 import Button, Dropdown
from widgetastic_patternfly4.ouia import (
    Button as PF4Button,
    ExpandableTable,
    PatternflyTable,
    Switch,
)

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixinPF4,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    EditableEntry,
    PF4ProgressBar,
    PF4Search,
    ReadOnlyEntry,
)

LOCATION_NUM = 3

class NewAddRemoveResourcesView(View):
    searchbox = PF4Search()
    type = Dropdown(
        locator='.//div[contains(@class, "All repositories") or'
        ' contains(@aria-haspopup="listbox")]'
    )
    Status = Dropdown(
        locator='.//div[contains(@class, "All") or contains(@aria-haspopup="listbox")]'
    )
    add_repo = PF4Button('OUIA-Generated-Button-secondary-2')
    # Need to add kebab menu
    table = PatternflyTable(
        component_id='OUIA-Generated-Table-4',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Type': Text('.//a'),
            'Name': Text('.//a'),
            'Product': Text('.//a'),
            'Sync State': Text('.//a'),
            'Content': Text('.//a'),
            'Status': Text('.//a'),
        },
    )

    def search(self, value):
        """Search for specific available resource and return the results"""
        self.searchbox.search(value)
        wait_for(
            lambda: self.table.is_displayed is True,
            timeout=60,
            delay=1,
        )
        self.table.wait_displayed()
        return self.table.read()

    def add(self, value):
        """Associate specific resource"""
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.add_repo.click()

    def fill(self, values):
        """Associate resource(s)"""
        if not isinstance(values, list):
            values = list((values,))
        for value in values:
            self.add(value)

    def remove(self, value):
        """Unassign some resource(s).
        :param str or list values: string containing resource name or a list of
            such strings.
        """
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.remove_button.click()

    def read(self):
        """Read all table values from both resource tables"""
        return self.table.read()


class ContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('.//h1[@data-ouia-component-id="cvPageHeaderText"]')
    create_content_view = PF4Button('create-content-view')
    table = ExpandableTable(
        component_id='content-views-table',
        column_widgets={
            'Name': Text('./a'),
            'Last task': Text('.//a'),
            'Latest version': Text('.//a'),
        },
    )

    @property
    def is_displayed(self):
        return self.create_content_view.is_displayed()


class ContentViewCreateView(BaseLoggedInView):
    title = Text('.//div[@data-ouia-component-id="create-content-view-modal"]')
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    submit = PF4Button('create-content-view-form-submit')
    cancel = PF4Button('create-content-view-form-cancel')

    @View.nested
    class component(View):
        component_tile = Text('//div[contains(@id, "component")]')
        solve_dependencies = Checkbox(id='dependencies')
        import_only = Checkbox(id='importOnly')

        def child_widget_accessed(self, widget):
            self.component_tile.click()

    @View.nested
    class composite(View):
        composite_tile = Text('//div[contains(@id, "composite")]')
        auto_publish = Checkbox(id='autoPublish')

        def child_widget_accessed(self, widget):
            self.composite_tile.click()

    @property
    def is_displayed(self):
        self.title.is_displayed()
        self.label.is_displayed()
        return True

    def after_fill(self, value):
        """Ensure 'Create content view' button is enabled after filling out the required fields"""
        self.submit.wait_displayed()


class ContentViewEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb('breadcrumbs-list')
    search = PF4Search()
    actions = ActionsDropdown(
        ".//button[contains(@id, 'toggle-dropdown')]"
    )
    publish = PF4Button('cv-details-publish-button')
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Content Views'

    @View.nested
    class details(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/details")]')
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        type = ReadOnlyEntry(name='Composite?')
        description = EditableEntry(name='Description')
        # depSolv is maybe a conditionalswitch
        solve_dependencies = Switch(name='solve_dependencies switch')
        import_only = Switch(name='import_only_switch')

    @View.nested
    class versions(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/versions")]')
        searchbox = PF4Search()
        table = PatternflyTable(
            component_id="content-view-versions-table",
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Version': Text('.//a'),
                'Environments': Text('.//a'),
                'Packages': Text('.//a'),
                'Errata': Text('.//a'),
                'Additional content': Text('.//a'),
                'Description': Text('.//a'),
                7: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )
        publishButton = PF4Button('cv-details-publish-button')

        def search(self, version_name):
            """Searches for content view version.
            Searchbox can't search by version name, only by number, that's why in
            case version name was passed, it's transformed into recognizable
            value before filling, for example::
                'Version 1.0' -> 'version = 1'
            """
            search_phrase = version_name
            if version_name.startswith('V') and '.' in version_name:
                search_phrase = f'version = {version_name.split()[1].split(".")[0]}'
            self.searchbox.search(search_phrase)
            return self.table.read()

    @View.nested
    class content_views(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/contentviews")]')

        resources = View.nested(NewAddRemoveResourcesView)

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/repositories")]')
        resources = View.nested(NewAddRemoveResourcesView)

    @View.nested
    class filters(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[contains(@href, "#/filters")]')
        new_filter = Text(".//button[@ui-sref='content-view.yum.filters.new']")


class ContentViewVersionPublishView(BaseLoggedInView):
    # publishing view is a popup so adding all navigation within the same context
    ROOT = './/div[contains(@class,"pf-c-wizard")]'
    title = Text(".//h2[contains(., 'Publish') and contains(@aria-label, 'Publish')]")
    # publishing screen
    description = TextInput(id='description')
    promote = Switch('promote-switch')

    # review screen only has info to review
    # shared buttons at bottom for popup for both push and review section
    next = Button('Next')
    finish = Button('Finish')
    back = Button('Back')
    cancel = Button('Cancel')
    close_button = Button('Close')
    progressbar = PF4ProgressBar('.//div[contains(@class, "pf-c-wizard__main-body")]')

    @property
    def is_displayed(self):
        return self.title.wait_displayed()

    def wait_animation_end(self):
        wait_for(
            lambda: 'in' in self.browser.classes(self),
            handle_exception=True,
            logger=self.logger,
            timeout=10,
        )

    def before_fill(self, values=None):
        """If we don't want to break view.fill() procedure flow, we need to
        push 'Edit' button to open necessary dialog to be able to fill values
        """
        self.promote.click()
        wait_for(
            lambda: self.lce.is_displayed is True,
            timeout=30,
            delay=1,
            logger=self.logger,
        )


class NewContentViewVersionDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and len(self.breadcrumb.locations) > LOCATION_NUM
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.locations[2] == 'Versions'
        )


