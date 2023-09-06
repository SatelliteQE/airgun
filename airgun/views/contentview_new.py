from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Tab
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4.ouia import Button as PF4Button
from widgetastic_patternfly4.ouia import ExpandableTable
from widgetastic_patternfly4.ouia import Switch
from widgetastic_patternfly4.ouia import PatternflyTable
from widgetastic_patternfly4.ouia import Modal

from airgun.views.common import BaseLoggedInView
from airgun.views.common import NewAddRemoveResourcesView
from airgun.views.common import SearchableViewMixinPF4
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import PF4Search
from airgun.widgets import ProgressBarPF4
from airgun.widgets import PF4LCESelector 
from airgun.widgets import ReadOnlyEntry
from airgun.widgets import SatTable
from airgun.views.common import BaseLoggedInView
from airgun.views.common import PF4LCESelectorGroup
from airgun.views.common import NewAddRemoveResourcesView
from airgun.views.common import SearchableViewMixinPF4
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import PF4Search
from airgun.widgets import ProgressBarPF4
from airgun.widgets import ReadOnlyEntry

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixinPF4


class NewContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('.//h1[@data-ouia-component-id="cvPageHeaderText"]')
    create_content_view = PF4Button('create-content-view')
    table = ExpandableTable(
        component_id='content-views-table',
        column_widgets={
            'Type': Text('./a'),
            'Name': Text('./a'),
            'Last Published': ('./a'),
            'Last task': Text('.//a'),
            'Latest version': Text('.//a'),
        },
    )

    @property
    def is_displayed(self):
        assert self.create_content_view.is_displayed()
        return True


class NewContentViewCreateView(BaseLoggedInView):
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


class NewContentViewEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    search = PF4Search()
    title = Text("//h2[contains(., 'Publish) or contains(@id, 'pf-wizard-title-0')]")
    actions = ActionsDropdown(
        "//div[contains(@data-ouia-component-id, 'OUIA-Generated-Dropdown-2')]"
    )
    publish = PF4Button('cv-details-publish-button')
    # not sure if this is needed
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and len(self.breadcrumb.locations) <= 3
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() != 'New Content View'
            and self.publish.is_displayed
        )

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
            Searchbox can't search by version name, only by id, that's why in
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


class NewContentViewVersionPublishView(BaseLoggedInView):
    # publishing view is a popup so adding all navigation within the same context
    breadcrumb = BreadCrumb()
    ROOT = './/div[contains(@class,"pf-c-wizard")]'
    title = Text("//h2[contains(., 'Publish' or contains(@id, 'pf-wizard-title-0')]")
    # publishing screen
    description = TextInput(id='description')
    promote = Switch('promote-switch')
    lce = ParametrizedView.nested(PF4LCESelectorGroup)

    # review screen only has info to review
    # shared buttons at bottom for popup for both push and review section
    next = Button('Next')
    finish = Button('Finish')
    back = Button('Back')
    cancel = Button('Cancel')
    close_button = Button('Close')
    progressbar = ProgressBarPF4()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() == 'Versions'
        )

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
            and len(self.breadcrumb.locations) > 3
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.locations[2] == 'Versions'
        )


class NewContentViewVersionPromote(View):
    """Promote CV Modal"""
    ROOT = './/div[@data-ouia-component-id="promote-version"]'
    description = TextInput(id='description')
    lce = ParametrizedView.nested(PF4LCESelectorGroup)
    promote = Button('Promote')
    cancel = Button('Cancel')
