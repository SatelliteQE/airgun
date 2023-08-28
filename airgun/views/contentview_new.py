from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4 import Switch
from widgetastic_patternfly4.ouia import BreadCrumb
from widgetastic_patternfly4.ouia import Button
from widgetastic_patternfly4.ouia import Dropdown
from widgetastic_patternfly4.ouia import ExpandableTable
from widgetastic_patternfly4.ouia import PatternflyTable

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixinPF4
from airgun.views.common import SatTab
from airgun.widgets import EditableEntry
from airgun.widgets import ReadOnlyEntry
from airgun.widgets import ProgressBarPF4
from airgun.widgets import PF4Search

class NewContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('.//h1[@data-ouia-component-id="cvPageHeaderText"]')
    create_content_view = Button('create-content-view')
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
        assert self.create_content_view.is_displayed()
        return True


class NewContentViewCreateView(BaseLoggedInView):
    title = Text('.//div[@data-ouia-component-id="create-content-view-modal"]')
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    submit = Button('create-content-view-form-submit')
    cancel = Button('create-content-view-form-cancel')

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
    """Inside a cv editable view that contains 'Details', 'Versions', 'Repo', 'Filters', and 'History'"""
    breadcrumb = BreadCrumb('cv-breadcrumb')
    title = Text('//h1[@data-ouia-component-id="cv-details-header-name"]')
    kebab = Dropdown(
        "//div[contains(@data-ouia-component-id, 'OUIA-Generated-Dropdown') or "
        "@data-ouia-component-type='PF4/Dropdown']"
    )
    publish = Button('cv-details-publish-button')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and len(self.breadcrumb.locations) <= 3
                and self.breadcrumb.locations[0] == 'Content Views'
                and self.breadcrumb.read() != 'New Content View'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        description = EditableEntry(name='Description')
        solve_dependencies = Switch(id='Solve Dependencies')

    @View.nested
    class versions(SatTab):
        searchbox = PF4Search
        table = PatternflyTable(
            component_id='content-view-versions-table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Version': Text('./a'),
                'Packages': Text('.//a'),
                'Errata': Text('.//a'),
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
    class repos(SatTab):
        pass

    @View.nested
    class filters(SatTab):
        pass


class NewContentViewPublishView(BaseLoggedInView):
    """Publish view is in a modal"""
    publish_modal = Text('.//div[contains(@data-ouia-component-id, "OUIA-Generated-Modal-large")]')
    title = Text('//h2[contains(@data-ouia-component-id, "OUIA-Generated-Title")]')
    # these buttons are on both pages
    next = Button('OUIA-Generated-Button-primary-1')
    finish = Button('OUIA-Generated-Button-primary-1')
    back = Button('OUIA-Generated-Button-secondary-1')
    cancel = Button('OUIA-Generated-Button-link-1')
    # second page of publish
    review_details = Text('//h2[contains(@data-ouia-component-id, "OUIA-Generated-Title")]')
    progressbar = ProgressBarPF4()

    @View.nested
    class publish_view(View):
        description = TextInput(id='description')
        promote = Switch(id='promote-switch')

    @View.nested
    class review_details(View):
    # TODO: May need to read the review details in publish if it's something we want as part of coverage
        pass

    @property
    def is_displayed(self):
        self.publish_modal.is_displayed()
        self.next.is_displayed()
        self.cancel.is_displayed()
        return True
