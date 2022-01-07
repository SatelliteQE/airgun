from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Checkbox
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly import Tab
from widgetastic_patternfly4.ouia import Button as PF4Button
from widgetastic_patternfly4.ouia import PatternflyTable
from widgetastic_patternfly4.ouia import Switch

from airgun.views.common import BaseLoggedInView
from airgun.views.common import LCESelectorGroup
from airgun.views.common import NewAddRemoveResourcesView
from airgun.views.common import SearchableViewMixinPF4
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import PF4Search
from airgun.widgets import ProgressBarPF4
from airgun.widgets import ReadOnlyEntry

class NewContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[contains(., 'Content Views')]")
    create_content_view = PF4Button('OUIA-Generated-Button-primary-1')
    table = PatternflyTable(
        component_id='OUIA-Generated-Table',
        column_widgets={
            'Name': Text('./a'),
            'Last Published': Text('./a'),
            'Last task': Text('.//a'),
            'Latest version': Text('.//a'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

class NewContentViewCreateView(BaseLoggedInView):
    title = Text("//h1[contains(., 'Create content view') or contains(@id, 'pf-modal-part-1')]")
    close_button = PF4Button('OUIA-Generated-Button-plain-8')
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    # cv and ccv are tiles
    component = Text('//div[contains(@id, "component")]')
    composite = Text('//div[contains(@id, "composite")]')
    solve_dependencies = Checkbox(id='dependencies')
    import_only = Checkbox(id='importOnly')
    auto_publish = Checkbox(id='auto_publish')
    submit = PF4Button('OUIA-Generated-Button-primary-2')
    cancel = PF4Button('OUA-Generated-Button-link-2')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.import_only, exception=False)

class ContentViewCopyView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    name = TextInput(id='name')
    copy_cv = PF4Button('OUIA-Generated-Button-primary-2')
    cancel = PF4Button('OUA-Generated-Button-link-2')

    @property
    def is_displayed(self):
        # most likely have to fix this
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and len(self.breadcrumb.locations) == 3
            and self.breadcrumb.read() == 'Copy'
        )

class NewContentViewDeleteView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    ROOT = './/div[contains(@class,"pf-c-wizard")]'
    title = Text("//h2[contains(., 'Publish' or contains(@id, 'pf-wizard-title-0')]")
    next = PF4Button('OUIA-Generated-Button-primary-2')
    delete = PF4Button('OUIA-Generated-Button-primary-2')
    back = PF4Button('OUIA-Generated-Button-secondary-2')
    cancel = PF4Button('OUA-Generated-Button-link-2')

class NewContentViewEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    search = PF4Search()
    title = Text("//h2[contains(., 'Publish) or contains(@id, 'pf-wizard-title-0')]")
    actions = ActionsDropdown("//div[contains(@data-ouia-component-id, 'OUIA-Generated-Dropdown-2')]")
    publish = PF4Button('OUIA-Generated-Button-primary-1')
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
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/details")]'
        )
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        type = ReadOnlyEntry(name='Composite?')
        description = EditableEntry(name='Description')
        # depSolv is maybe a conditionalswitch
        solve_dependencies = Switch(name='solve_dependencies switch')
        import_only = Switch(name='import_only_switch')

    @View.nested
    class versions(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/versions")]'
        )
        searchbox = PF4Search()
        table = PatternflyTable(
            #component_id='OUIA-Generated-Table',
            column_widgets={
                'Version': Text('.//a'),
                'Environments': Text('.//a'),
                'Packages': Text('.//a'),
                'Additional content': Text('.//a'),
                'Description': Text('.//a'),
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
                search_phrase = f'version = {version_name.split()[1].split(".")[0]}'
            self.searchbox.search(search_phrase)
            return self.table.read()

    @View.nested
    class content_views(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/contentviews")]'
        )

        resources = View.nested(NewAddRemoveResourcesView)

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/repositories")]'
        )
        resources = View.nested(NewAddRemoveResourcesView)

    @View.nested
    class filters(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[contains(@href, "#/filters")]'
        )
        new_filter = Text(".//button[@ui-sref='content-view.yum.filters.new']")

class NewContentViewVersionPublishView(BaseLoggedInView):
    # publishing view is a popup so adding all navigation within the same context
    breadcrumb = BreadCrumb()
    ROOT = './/div[contains(@class,"pf-c-wizard")]'
    title = Text("//h2[contains(., 'Publish' or contains(@id, 'pf-wizard-title-0')]")
    # publishing screen
    description = TextInput(id='description')
    #use either promote-switch or OUIA-Generated-Switch-1
    promote = Switch('promote-switch')

    # need to fix this for publish_and_promote
    lce = Checkbox(locator=".//input[contains(@data-ouia-component-id, 'OUIA-Generated-Checkbox-2')]")
    # review screen only has info to review
    # shared buttons at bottom for popup for both push and review section
    next = PF4Button('OUIA-Generated-Button-primary-1')
    finish = PF4Button('OUIA-Generated-Button-primary-1')
    back = PF4Button('OUIA-Generated-Button-secondary-1')
    cancel = PF4Button('OUIA-Generated-Button-link-1')
    close_button = PF4Button('OUIA-Generated-Button-primary-2')
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
        description = EditableEntry(name='Description')
        return (
            breadcrumb_loaded
            and len(self.breadcrumb.locations) > 3
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.locations[2] == 'Versions'
        )

class NewContentViewVersionPromoteView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    lce = ParametrizedView.nested(LCESelectorGroup)
    description = TextInput(id='description')
    promote = PF4Button(id='OUIA-Generated-Button-primary-1')
    cancel = PF4Button(id='OUIA-Generated-Button-link-1')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Views'
            and self.breadcrumb.read() == 'Promotion'
        )

    def after_fill(self, was_change):
        """To get promote button to be enabled, ensure we choose an LCE first"""
        wait_for(
            lambda: self.promote.is_displayed is True,
            timeout=30,
            delay=1,
            logger=self.logger,
        )