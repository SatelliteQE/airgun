from widgetastic.exceptions import NoSuchElementException
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, TextInput, View, Widget
from widgetastic_patternfly import Tab
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Modal as PF5Modal,
)
from widgetastic_patternfly5.ouia import (
    Dropdown as PF5OUIADropdown,
    PatternflyTable as PF5OUIATable,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class ContentCredentialsTableView(BaseLoggedInView, SearchableViewMixin):
    """PF5 list page for Content Credentials at /labs/content_credentials."""

    title = Text('//h1[normalize-space(.)="Content Credentials"]')
    table = PF5OUIATable(
        component_id='content-credentials-table',
        column_widgets={
            'Name': Text('./a'),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.table.is_displayed


class ContentCredentialCreateView(BaseLoggedInView):
    # Not yet implemented in React UI
    pass


class DetailField(Widget):
    """A field in a PF5 description list (dt/dd pair).

    Locates a ``<dt>``/``<dd>`` pair by the label text in the ``<dt>`` element.
    """

    def __init__(self, parent, label, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = label

    def _dd_locator(self):
        return f'.//dt[normalize-space(.)="{self.label}"]/following-sibling::dd[1]'

    @property
    def is_displayed(self):
        try:
            self.browser.element(self._dd_locator())
            return True
        except NoSuchElementException:
            return False

    def read(self):
        """Return the text content of the ``<dd>`` element."""
        dd = self.browser.element(self._dd_locator())
        return self.browser.text(dd).strip()

    def __locator__(self):
        return self._dd_locator()


class DeleteContentCredentialModal(PF5Modal):
    """PF5 confirmation modal for deleting a Content Credential."""

    ROOT = './/div[@data-ouia-component-id="delete-content-credential-modal"]'

    confirm_delete = PF5Button(locator='.//button[@data-ouia-component-id="delete-confirm-button"]')
    cancel = PF5Button(locator='.//button[@data-ouia-component-id="delete-cancel-button"]')

    @property
    def is_displayed(self):
        return self.confirm_delete.is_displayed


class ContentCredentialEditView(BaseLoggedInView):
    """PF5 details page for a Content Credential at /labs/content_credentials/:id."""

    title = Text('.//h1[@data-ouia-component-id="credential-details-header-name"]')

    # Action buttons
    view_tasks = PF5Button(
        locator='.//a[@data-ouia-component-id="credential-details-view-tasks-button"]'
    )
    actions = PF5OUIADropdown(component_id='credential-details-actions')

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.details.is_displayed

    @View.nested
    class details(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[@data-ouia-component-id="routed-tabs-tab-details"]')

        name = DetailField(label='Name')
        content_type = DetailField(label='Type')
        content = DetailField(label='Content')
        upload_file = PF5Button(locator='.//button[@data-ouia-component-id="upload-file-button"]')
        products = DetailField(label='Products')
        repositories = DetailField(label='Repositories')
        alternate_content_sources = DetailField(label='Alternate content sources')

    @View.nested
    class products(Tab):
        TAB_LOCATOR = ParametrizedLocator('//a[@data-ouia-component-id="routed-tabs-tab-products"]')

        empty_state = Text(
            './/div[@data-ouia-component-id="products-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = TextInput(
            locator='.//input[@data-ouia-component-id="products-filter-input"]'
        )
        table = PF5OUIATable(
            component_id='content-credential-products-table',
            column_widgets={'Name': Text('./a')},
        )

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[@data-ouia-component-id="routed-tabs-tab-repositories"]'
        )

        empty_state = Text(
            './/div[@data-ouia-component-id="repositories-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = TextInput(
            locator='.//input[@data-ouia-component-id="repositories-filter-input"]'
        )
        table = PF5OUIATable(component_id='content-credential-repositories-table')

    @View.nested
    class alternate_content_sources(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//a[@data-ouia-component-id="routed-tabs-tab-alternate_content_sources"]'
        )

        empty_state = Text(
            './/div[@data-ouia-component-id="acs-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = TextInput(locator='.//input[@data-ouia-component-id="acs-filter-input"]')
        table = PF5OUIATable(component_id='content-credential-acs-table')
