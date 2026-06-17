from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, TextInput, View
from widgetastic_patternfly import Tab
from widgetastic_patternfly5.components.forms.form_select import FormSelect
from widgetastic_patternfly5.ouia import (
    BreadCrumb as PF5OUIABreadCrumb,
    Button as PF5OUIAButton,
    Dropdown as PF5OUIADropdown,
    Modal as PF5OUIAModal,
    PatternflyTable as PF5OUIATable,
    TextInput as PF5OUIATextInput,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import PF5EditableSpacedListItem, PF5SpacedListItem


class ContentCredentialsTableView(BaseLoggedInView, SearchableViewMixinPF4):
    """PF5 list page for Content Credentials at /labs/content_credentials."""

    title = Text('//h1[normalize-space(.)="Content Credentials"]')
    create_button = PF5OUIAButton('action-buttons-create')
    table = PF5OUIATable(
        component_id='content-credentials-table',
        column_widgets={
            'Name': Text('./a'),
        },
    )

    @property
    def is_displayed(self):
        return (
            self.title.is_displayed and self.table.is_displayed and self.create_button.is_displayed
        )


class CreateContentCredentialModal(PF5OUIAModal):
    """PF5 confirmation modal for creating a Content Credential."""

    OUIA_ID = 'create-content-credential-modal'

    name_input = PF5OUIATextInput('create-content-credential-name-input')
    content_type = FormSelect(locator='.//select[@id="content_type"]')
    content_text_box = TextInput(locator='.//textarea[@aria-label="content"]')
    create_button = PF5OUIAButton('create-content-credential-create-button')
    cancel_button = PF5OUIAButton('create-content-credential-cancel-button')

    @property
    def is_displayed(self):
        return self.name_input.is_displayed


class DeleteContentCredentialModal(PF5OUIAModal):
    """PF5 confirmation modal for deleting a Content Credential."""

    OUIA_ID = 'delete-content-credential-modal'

    confirm_delete = PF5OUIAButton('delete-content-credential-delete-button')
    cancel = PF5OUIAButton('delete-content-credential-cancel-button')

    @property
    def is_displayed(self):
        return self.confirm_delete.is_displayed


class ContentCredentialEditView(BaseLoggedInView):
    """PF5 details page for a Content Credential at /labs/content_credentials/:id."""

    title = Text('.//h1[@data-ouia-component-id="credential-details-header-name"]')
    page_breadcrumb = PF5OUIABreadCrumb('content-credential-breadcrumb')

    # Action buttons
    view_tasks = PF5OUIAButton('credential-details-view-tasks-button')
    actions = PF5OUIADropdown(component_id='credential-details-actions')

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.details.is_displayed

    @View.nested
    class details(Tab):
        TAB_LOCATOR = ParametrizedLocator('//*[@data-ouia-component-id="routed-tabs-tab-details"]')

        name = PF5EditableSpacedListItem(label='Name')
        content_type = PF5SpacedListItem(label='Type')
        content = PF5SpacedListItem(label='Content')
        upload_file = PF5OUIAButton('upload-file-button')
        products = PF5SpacedListItem(label='Products')
        repositories = PF5SpacedListItem(label='Repositories')
        alternate_content_sources = PF5SpacedListItem(label='Alternate content sources')

    @View.nested
    class products(Tab):
        TAB_LOCATOR = ParametrizedLocator('//*[@data-ouia-component-id="routed-tabs-tab-products"]')

        empty_state = Text(
            './/div[@data-ouia-component-id="products-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = PF5OUIATextInput('products-filter-input')
        table = PF5OUIATable(
            component_id='content-credential-products-table',
            column_widgets={'Name': Text('./a')},
        )

    @View.nested
    class repositories(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//*[@data-ouia-component-id="routed-tabs-tab-repositories"]'
        )

        empty_state = Text(
            './/div[@data-ouia-component-id="repositories-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = PF5OUIATextInput('repositories-filter-input')
        table = PF5OUIATable(component_id='content-credential-repositories-table')

    @View.nested
    class alternate_content_sources(Tab):
        TAB_LOCATOR = ParametrizedLocator(
            '//*[@data-ouia-component-id="routed-tabs-tab-alternate_content_sources"]'
        )

        empty_state = Text(
            './/div[@data-ouia-component-id="acs-empty-state-card"]'
            '//*[contains(@class, "pf-v5-c-empty-state__body")]'
        )
        filter_input = PF5OUIATextInput('acs-filter-input')
        table = PF5OUIATable(component_id='content-credential-acs-table')
