from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4.ouia import Button as PF4Button
from widgetastic_patternfly4.ouia import ExpandableTable

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixinPF4


class NewContentViewTableView(BaseLoggedInView, SearchableViewMixinPF4):
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
