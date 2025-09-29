from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly4 import (
    Button,
    Drawer,
    Dropdown,
    FormSelect,
    Pagination as PF4Pagination,
    Radio,
    Switch,
)
from widgetastic_patternfly4.ouia import (
    Button as OUIAButton,
    FormSelect as OUIAFormSelect,
    PatternflyTable,
    Switch as OUIASwitch,
    Text as OUIAText,
    TextInput as OUIATextInput,
)

from airgun.views.common import BaseLoggedInView, WizardStepView
from airgun.widgets import DualListSelector, EditModal, ItemsList, SearchInput


class EditDetailsModal(EditModal):
    """Class representing the Edit Details modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-details-modal"]'

    name = OUIATextInput('acs-edit-name-field')
    description = TextInput(locator='.//textarea[@id="acs_description_field"]')

    edit_button = OUIAButton('edit-acs-details-submit')
    cancel_button = OUIAButton('edit-acs-details-cancel')


class EditCapsulesModal(DualListSelector):
    """Class representing the Edit Capsule modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-smart-proxies-modal"]'

    use_http_proxies = Switch(locator='.//label[@for="use-http-proxies-switch"]')

    edit_button = OUIAButton('edit-acs-smart-proxies-submit')
    cancel_button = OUIAButton('edit-acs-smart-proxies-cancel')


class EditUrlAndSubpathsModal(EditModal):
    """Class repsenting the Edit URL and Subpaths modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-url-paths-modal"]'

    base_url = OUIATextInput('acs-base-url-field')
    url_err = Text('.//div[contains(@id, "acs_base_url-helper")]')
    subpaths = TextInput(locator='.//textarea[@id="acs_subpath_field"]')
    paths_err = Text('.//div[contains(@id, "acs_subpaths-helper")]')

    edit_button = OUIAButton('edit-acs-url-submit')
    cancel_button = OUIAButton('edit-acs-url-cancel')


class EditCredentialsModal(EditModal):
    """Class representing the Edit Credentials modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-credentials-modal"]'

    verify_ssl_toggle = Switch(locator='.//label[@for="verify-ssl-switch"]')
    select_ca_cert = OUIAFormSelect('sslCAcert-select')

    manual_auth_radio_btn = Radio(id='manual_auth')
    username = OUIATextInput('acs-username-field')
    password = OUIATextInput('acs-password-field')

    content_credentials_radio_btn = Radio(id='content_credentials')
    ssl_client_cert = OUIAFormSelect('ssl-client-cert-select')
    ssl_client_key = OUIAFormSelect('ssl_client_key_select')

    none_auth_radio_btn = Radio(id='none')

    edit_button = OUIAButton('edit-acs-credentials-submit')
    cancel_button = OUIAButton('edit-acs-credentials-cancel')


class EditProductsModal(DualListSelector):
    """Class representing the Edit Products modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-products-modal"]'

    edit_button = OUIAButton('edit-acs-products-submit')
    cancel_button = OUIAButton('edit-acs-products-cancel')


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

    title = Text('.//h2[contains(@class, "pf-c-title")]')
    close_modal = Button(locator='.//button[@aria-label="Close"]')

    @View.nested
    class select_source_type(WizardStepView):
        expander = Text('.//button[contains(.,"Select source type")]')
        custom_option = Text('//*[@id="custom"]')
        simplified_option = Text('//*[@id="simplified"]')
        rhui_option = Text('//*[@id="rhui"]')
        content_type_select = OUIAFormSelect('content-type-select')

    @View.nested
    class name_source(WizardStepView):
        expander = Text('.//button[contains(.,"Name source")]')
        name = OUIATextInput('acs_name_field')
        description = TextInput(locator='.//textarea[@id="acs_description_field"]')

    @View.nested
    class select_capsule(WizardStepView, DualListSelector):
        expander = Text(
            './/button[contains(.,"Select Smart proxy") or contains(.,"Select Capsule")]'
        )
        use_http_proxies = OUIASwitch('use-http-proxies-switch')

    @View.nested
    class url_and_paths(WizardStepView):
        expander = Text('.//button[contains(.,"URL and paths")]')
        base_url = OUIATextInput('acs_base_url_field')
        url_err = Text('.//div[contains(@id, "acs_base_url-helper")]')
        subpaths = TextInput(locator='.//textarea[@id="acs_subpath_field"]')
        paths_err = Text('.//div[contains(@id, "acs_subpaths-helper")]')

    @View.nested
    class credentials(WizardStepView):
        expander = Text('.//button[contains(.,"Credentials")]')
        verify_ssl_toggle = OUIASwitch('verify-ssl-switch')
        select_ca_cert = FormSelect(locator='.//select[option[text()="Select a CA certificate"]]')

        manual_auth_radio_btn = Radio(id='manual_auth')
        username = OUIATextInput('acs_username_field')
        password = OUIATextInput('acs_password_field')

        content_credentials_radio_btn = Radio(id='content_credentials')
        ssl_client_cert = OUIAFormSelect('sslCert-select')
        ssl_client_key = OUIAFormSelect('sslKey-select')

        none_auth_radio_btn = Radio(id='none')

    @View.nested
    class select_products(WizardStepView, DualListSelector):
        expander = Text('.//button[contains(.,"Select products")]')

    @View.nested
    class review_details(WizardStepView):
        expander = Text('.//button[contains(.,"Review details")]')
        add_button = Button(locator='.//button[normalize-space(.)="Add"]')
        cancel_button = Button(locator='.//button[normalize-space(.)="Cancel"]')


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

    title = OUIAText('acs-name-text')
    refresh_resource = OUIAButton('refresh-acs')
    kebab_menu = Dropdown(locator='//button[contains(@aria-label, "details_actions")]')
    last_refresh = Text('//dd[contains(@aria-label, "last_refresh_text_value")]')

    @View.nested
    class details(View, AcsStackItem):
        """Class representing the Details stack item in the ACS drawer."""

        ROOT = '//div[normalize-space(.)="Details" and contains(@class, "pf-c-expandable-section")]'

        title = OUIAText('expandable-details-text')
        edit_details = Button(locator='//button[contains(@aria-label, "edit-details-pencil-edit")]')

        @View.nested
        class details_stack_content(View):
            """Class representing content of the Details stack item."""

            ROOT = '//div[@id="showDetails"]'

            name = Text('//dd[@aria-label="name_text_value"]')
            description = Text('//dd[@aria-label="description_text_value"]')
            type = Text('//dd[@aria-label="type_text_value"]')
            content_type = Text('//dd[@aria-label="content_type_text_value"]')

    @View.nested
    class capsules(View, AcsStackItem):
        """Class representing the Capsules stack item in the ACS drawer"""

        ROOT = (
            '//div[(normalize-space(.)="Capsules") and contains(@class, "pf-c-expandable-section")]'
        )
        title = OUIAText('expandable-smart-proxies-text')
        edit_capsules = Button(
            locator='//button[contains(@aria-label, "edit-smart-proxies-pencil-edit")]'
        )

        @View.nested
        class capsules_stack_content(View):
            """Class representing content of the Capsules stack item."""

            ROOT = '//div[@id="showSmartProxies"]'

            capsules_list = ItemsList(locator='.//ul[contains(@class, "pf-c-list")]')
            use_http_proxies = Text('//dd[@aria-label="useHttpProxies_value"]')

    @View.nested
    class url_and_subpaths(View, AcsStackItem):
        """
        Class representing the URL and subpaths stack item in the ACS drawer.
        Present only if ACS is of type 'Custom' or 'RHUI'.
        """

        ROOT = (
            '//div[normalize-space(.)="URL and subpaths" '
            'and contains(@class, "pf-c-expandable-section")]'
        )

        title = OUIAText('expandable-url-paths-text')
        edit_url_and_subpaths = Button(
            locator='//button[contains(@aria-label, "edit-urls-pencil-edit")]'
        )

        @View.nested
        class url_and_subpaths_stack_content(View):
            """Class representing content of the URL and subpaths stack item."""

            ROOT = '//div[@id="showUrlPaths"]'

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
            'and contains(@class, "pf-c-expandable-section")]'
        )

        title = OUIAText('expandable-credentials-text')
        edit_credentials = Button(
            locator='//button[contains(@aria-label, "edit-credentials-pencil-edit")]'
        )

        @View.nested
        class credentials_stack_content(View):
            """Class representing content of the Credentials stack item."""

            ROOT = '//div[@id="showCredentials"]'

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

        ROOT = (
            '//div[normalize-space(.)="Products" and contains(@class, "pf-c-expandable-section")]'
        )

        title = OUIAText('expandable-products-text')
        edit_products = Button(
            locator='//button[contains(@aria-label, "edit-products-pencil-edit")]'
        )

        @View.nested
        class products_stack_content(View):
            """Class representing content of the Products stack item."""

            ROOT = '//div[@id="showProducts"]'

            products_list = ItemsList(locator='.//ul[contains(@class, "pf-c-list")]')


class AlternateContentSourcesView(BaseLoggedInView):
    """Class that describes view of the Alternate Content Sources page."""

    title = Text('//h1[contains(., "Alternate Content Sources")]')
    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')

    @View.nested
    class acs_drawer(Drawer):
        """Class that describes drawer of the Alternate Content Sources page"""

        select_all = Checkbox(locator='//input[contains(@aria-label, "Select all")]')
        search_bar = SearchInput(locator='.//div[contains(@class, "pf-c-input-group")]//input')
        clear_search_btn = Button(locator='//button[@aria-label="Reset search"]')
        add_source = OUIAButton('create-acs')
        kebab_menu = Dropdown(
            locator='.//div[contains(@data-ouia-component-id, "acs-bulk-actions")]'
        )

        content_table = PatternflyTable(
            component_id='alternate-content-sources-table',
            column_widgets={
                0: Checkbox(locator='.//input[@type="checkbox"]'),
                'Name': Text('.//a[contains(@data-ouia-component-id, "acs-link-text-")]'),
                'Type': Text('.//td[3]'),
                'LastRefresh': Text('.//td[4]'),
                4: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )

        clear_search = OUIAButton('empty-state-secondary-action-router-link')
        pagination = PF4Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
