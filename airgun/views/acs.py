from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Drawer as PF5Drawer,
    Dropdown as PF5Dropdown,
    FormSelect as PF5FormSelect,
    Pagination as PF5Pagination,
    Radio as PF5Radio,
    Switch as PF5Switch,
)
from widgetastic_patternfly5.ouia import (
    Button as PF5OUIAButton,
    FormSelect as PF5OUIAFormSelect,
    PatternflyTable as PF5OUIAPatternflyTable,
    Switch as PF5OUIASwitch,
    Text as PF5OUIAText,
    TextInput as PF5OUIATextInput,
)

from airgun.views.common import BaseLoggedInView, WizardStepView
from airgun.widgets import DualListSelector, EditModal, ItemsList, SearchInput


class EditDetailsModal(EditModal):
    """Class representing the Edit Details modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-details-modal"]'

    name = PF5OUIATextInput('acs-edit-name-field')
    description = TextInput(locator='.//textarea[@id="acs_description_field"]')

    edit_button = PF5OUIAButton('edit-acs-details-submit')
    cancel_button = PF5OUIAButton('edit-acs-details-cancel')


class EditCapsulesModal(DualListSelector):
    """Class representing the Edit Capsule modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-smart-proxies-modal"]'

    use_http_proxies = PF5Switch(locator='.//label[@for="use-http-proxies-switch"]')

    edit_button = PF5OUIAButton('edit-acs-smart-proxies-submit')
    cancel_button = PF5OUIAButton('edit-acs-smart-proxies-cancel')


class EditUrlAndSubpathsModal(EditModal):
    """Class repsenting the Edit URL and Subpaths modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-url-paths-modal"]'

    base_url = PF5OUIATextInput('acs-base-url-field')
    url_err = Text('.//div[contains(@id, "acs_base_url-helper")]')
    subpaths = TextInput(locator='.//textarea[@id="acs_subpath_field"]')
    paths_err = Text('.//div[contains(@id, "acs_subpaths-helper")]')

    edit_button = PF5OUIAButton('edit-acs-url-submit')
    cancel_button = PF5OUIAButton('edit-acs-url-cancel')


class EditCredentialsModal(EditModal):
    """Class representing the Edit Credentials modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-credentials-modal"]'

    verify_ssl_toggle = PF5Switch(locator='.//label[@for="verify-ssl-switch"]')
    select_ca_cert = PF5OUIAFormSelect('sslCAcert-select')

    manual_auth_radio_btn = PF5Radio(id='manual_auth')
    username = PF5OUIATextInput('acs-username-field')
    password = PF5OUIATextInput('acs-password-field')

    content_credentials_radio_btn = PF5Radio(id='content_credentials')
    ssl_client_cert = PF5OUIAFormSelect('ssl-client-cert-select')
    ssl_client_key = PF5OUIAFormSelect('ssl_client_key_select')

    none_auth_radio_btn = PF5Radio(id='none')

    edit_button = PF5OUIAButton('edit-acs-credentials-submit')
    cancel_button = PF5OUIAButton('edit-acs-credentials-cancel')


class EditProductsModal(DualListSelector):
    """Class representing the Edit Products modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-products-modal"]'

    edit_button = PF5OUIAButton('edit-acs-products-submit')
    cancel_button = PF5OUIAButton('edit-acs-products-cancel')


class AddAlternateContentSourceModal(View):
    """
    Class representing the "Add Alternate Content Source" modal.
    It contains multiple nested classes each representing a step of the wizard.

    There are two variations of wizard steps depending on selected source type:

    * Select source type
    * Name source
    * Select Capsule

    @ Simplified:
        * Select products

    @ Custom, RHUI:
        * URL and paths
        * Credentials

    * Review details
    """

    ROOT = '//div[contains(@data-ouia-component-id, "OUIA-Generated-Modal-large-")]'

    title = PF5OUIAText('wizard-header-text')
    close_modal = PF5Button(locator='.//button[@aria-label="Close"]')

    @View.nested
    class select_source_type(WizardStepView):
        expander = Text('.//button[contains(.,"Select source type")]')
        custom_option = Text('//*[@id="custom"]')
        simplified_option = Text('//*[@id="simplified"]')
        rhui_option = Text('//*[@id="rhui"]')
        content_type_select = PF5OUIAFormSelect('content-type-select')

    @View.nested
    class name_source(WizardStepView):
        expander = Text('.//button[contains(.,"Name source")]')
        name = PF5OUIATextInput('acs_name_field')
        description = TextInput(locator='.//textarea[@id="acs_description_field"]')

    @View.nested
    class select_capsule(WizardStepView, DualListSelector):
        expander = Text(
            './/button[contains(.,"Select Smart proxy") or contains(.,"Select Capsule")]'
        )
        use_http_proxies = PF5OUIASwitch('use-http-proxies-switch')

    @View.nested
    class url_and_paths(WizardStepView):
        expander = Text('.//button[contains(.,"URL and paths")]')
        base_url = PF5OUIATextInput('acs_base_url_field')
        url_err = Text('.//div[contains(@id, "acs_base_url-helper")]')
        subpaths = TextInput(locator='.//textarea[@id="acs_subpath_field"]')
        paths_err = Text('.//div[contains(@id, "acs_subpaths-helper")]')

    @View.nested
    class credentials(WizardStepView):
        expander = Text('.//button[contains(.,"Credentials")]')
        verify_ssl_toggle = PF5OUIASwitch('verify-ssl-switch')
        select_ca_cert = PF5FormSelect(
            locator='.//select[option[text()="Select a CA certificate"]]'
        )

        manual_auth_radio_btn = PF5Radio(id='manual_auth')
        username = PF5OUIATextInput('acs_username_field')
        password = PF5OUIATextInput('acs_password_field')

        content_credentials_radio_btn = PF5Radio(id='content_credentials')
        ssl_client_cert = PF5OUIAFormSelect('sslCert-select')
        ssl_client_key = PF5OUIAFormSelect('sslKey-select')

        none_auth_radio_btn = PF5Radio(id='none')

    @View.nested
    class select_products(WizardStepView, DualListSelector):
        expander = Text('.//button[contains(.,"Select products")]')

    @View.nested
    class review_details(WizardStepView):
        expander = Text('.//button[contains(.,"Review details")]')
        add_button = PF5Button(locator='.//button[normalize-space(.)="Add"]')
        cancel_button = PF5Button(locator='.//button[normalize-space(.)="Cancel"]')


class AcsStackItem:
    """
    Class containing basic properties and methods
    for stack item in the ACS drawer.
    """

    @property
    def is_expanded(self):
        """Returns True if the Details stack item is expanded."""
        return 'pf-m-expanded' in self.browser.classes(self.ROOT)

    def expand(self):
        """Expands the Details stack item."""
        if not self.is_expanded:
            self.browser.click(self.title)

    def collapse(self):
        """Collapses the stack item."""
        if self.is_expanded:
            self.browser.click(self.title)


class RowDrawer(View):
    """
    Class that describes row drawer of the Alternate Content Sources page.
    Drawer can contain following items depending on the type of the ACS:

        * Details:           [Simplified, Custom, RHUI]
        * Capsules:          [Simplified, Custom, RHUI]
        * URL and subpaths:  [Custom, RHUI]
        * Credentials:       [Custom, RHUI]
        * Products:          [Simplified]

    """

    title = PF5OUIAText('acs-name-text')
    refresh_resource = PF5OUIAButton('refresh-acs')
    kebab_menu = PF5Dropdown(locator='//button[contains(@aria-label, "details_actions")]')
    last_refresh = Text('//dd[contains(@aria-label, "last_refresh_text_value")]')

    @View.nested
    class details(View, AcsStackItem):
        """Class representing the Details stack item in the ACS drawer."""

        ROOT = (
            '//div[normalize-space(.)="Details" and contains(@class, "pf-v5-c-expandable-section")]'
        )

        title = PF5OUIAText('expandable-details-text')
        edit_details = PF5Button(
            locator='//button[contains(@aria-label, "edit-details-pencil-edit")]'
        )

        @View.nested
        class details_stack_content(View):
            """Class representing content of the Details stack item."""

            ROOT = '//div[@id="showDetails-content"]'

            name = Text('//dd[@aria-label="name_text_value"]')
            description = Text('//dd[@aria-label="description_text_value"]')
            type = Text('//dd[@aria-label="type_text_value"]')
            content_type = Text('//dd[@aria-label="content_type_text_value"]')

    @View.nested
    class capsules(View, AcsStackItem):
        """Class representing the Capsules stack item in the ACS drawer"""

        ROOT = (
            '//div[(normalize-space(.)="Capsules")'
            ' and contains(@class, "pf-v5-c-expandable-section")]'
        )
        title = PF5OUIAText('expandable-smart-proxies-text')
        edit_capsules = PF5Button(
            locator='//button[contains(@aria-label, "edit-smart-proxies-pencil-edit")]'
        )

        @View.nested
        class capsules_stack_content(View):
            """Class representing content of the Capsules stack item."""

            ROOT = '//div[@id="showSmartProxies-content"]'

            capsules_list = ItemsList(locator='.//ul[contains(@class, "pf-v5-c-list")]')
            use_http_proxies = Text('//dd[@aria-label="useHttpProxies_value"]')

    @View.nested
    class url_and_subpaths(View, AcsStackItem):
        """
        Class representing the URL and subpaths stack item in the ACS drawer.
        Present only if ACS is of type 'Custom' or 'RHUI'.
        """

        ROOT = (
            '//div[normalize-space(.)="URL and subpaths" '
            'and contains(@class, "pf-v5-c-expandable-section")]'
        )

        title = PF5OUIAText('expandable-url-paths-text')
        edit_url_and_subpaths = PF5Button(
            locator='//button[contains(@aria-label, "edit-urls-pencil-edit")]'
        )

        @View.nested
        class url_and_subpaths_stack_content(View):
            """Class representing content of the URL and subpaths stack item."""

            ROOT = '//div[@id="showUrlPaths-content"]'

            url = Text('//dd[@aria-label="url_text_value"]')
            subpaths = Text('//dd[@aria-label="subpaths_text_value"]')

    @View.nested
    class credentials(View, AcsStackItem):
        """
        Class representing the Credentials stack item in the ACS drawer.
        Present only if ACS is of type 'Custom' or 'RHUI'.
        """

        ROOT = (
            '//div[normalize-space(.)="Credentials" '
            'and contains(@class, "pf-v5-c-expandable-section")]'
        )

        title = PF5OUIAText('expandable-credentials-text')
        edit_credentials = PF5Button(
            locator='//button[contains(@aria-label, "edit-credentials-pencil-edit")]'
        )

        @View.nested
        class credentials_stack_content(View):
            """Class representing content of the Credentials stack item."""

            ROOT = '//div[@id="showCredentials-content"]'

            verify_ssl = Text('//dd[@aria-label="verifySSL_value"]')
            ssl_ca_certificate = Text('//dd[@aria-label="sslCaCert_value"]')
            ssl_client_certificate = Text('//dd[@aria-label="sslClientCert_value"]')
            ssl_client_key = Text('//dd[@aria-label="sslClientKey_value"]')
            username = Text('//dd[@aria-label="username_value"]')
            password = Text('//dd[@aria-label="password_value"]')

    @View.nested
    class products(View, AcsStackItem):
        """
        Class representing the Products stack item in the ACS drawer.
        Present only if ACS is of type 'Simplified'.
        """

        ROOT = '//div[normalize-space(.)="Products" and contains(@class, "pf-v5-c-expandable-section")]'

        title = PF5OUIAText('expandable-products-text')
        edit_products = PF5Button(
            locator='//button[contains(@aria-label, "edit-products-pencil-edit")]'
        )

        @View.nested
        class products_stack_content(View):
            """Class representing content of the Products stack item."""

            ROOT = '//div[@id="showProducts-content"]'

            products_list = ItemsList(locator='.//ul[contains(@class, "pf-v5-c-list")]')


class AlternateContentSourcesView(BaseLoggedInView):
    """Class that describes view of the Alternate Content Sources page."""

    title = Text('//h1[contains(., "Alternate Content Sources")]')
    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')
    blank_page = Text("//div[contains(@class, 'pf-v5-c-empty-state')]")

    @View.nested
    class acs_drawer(PF5Drawer):
        """Class that describes drawer of the Alternate Content Sources page"""

        select_all = Checkbox(locator='//input[contains(@aria-label, "Select all")]')
        search_bar = SearchInput(locator='.//div[contains(@class, "pf-v5-c-input-group")]//input')
        clear_search_btn = PF5Button(locator='//button[@aria-label="Reset search"]')
        add_source = PF5OUIAButton('create-acs')
        kebab_menu = PF5Dropdown(
            locator='.//div[contains(@data-ouia-component-id, "acs-bulk-actions")]'
        )

        content_table = PF5OUIAPatternflyTable(
            component_id='alternate-content-sources-table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//a[contains(@data-ouia-component-id, "acs-link-text-")]'),
                'Type': Text('.//td[3]'),
                'LastRefresh': Text('.//td[4]'),
                4: PF5Dropdown(locator='.//div[contains(@class, "pf-v5-c-dropdown")]'),
            },
        )

        clear_search = PF5OUIAButton('empty-state-secondary-action-router-link')
        pagination = PF5Pagination()

    @property
    def is_displayed(self):
        blank_page = self.browser.wait_for_element(self.blank_page, exception=False) is not None
        table = (
            self.browser.wait_for_element(self.acs_drawer.content_table, exception=False)
            is not None
        )
        return blank_page or table
