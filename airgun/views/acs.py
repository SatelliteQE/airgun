import time

from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Drawer
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import FormSelect
from widgetastic_patternfly4 import Pagination
from widgetastic_patternfly4 import Radio
from widgetastic_patternfly4 import Switch
from widgetastic_patternfly4.ouia import Button as OUIAButton
from widgetastic_patternfly4.ouia import FormSelect as OUIAFormSelect
from widgetastic_patternfly4.ouia import PatternflyTable
from widgetastic_patternfly4.ouia import Switch as OUIASwitch
from widgetastic_patternfly4.ouia import Text as OUIAText
from widgetastic_patternfly4.ouia import TextInput as OUIATextInput

from airgun.views.common import BaseLoggedInView
from airgun.views.common import WizardStepView
from airgun.views.host_new import SearchInput
from airgun.widgets import ItemsList


class EditModal(View):
    """Class representing the Edit modal header"""

    title = Text('.//h1')
    close_button = OUIAButton('acs-edit-details-modal-ModalBoxCloseButton')

    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')


class EditDetailsModal(EditModal):
    """Class representing the Edit Details modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-details-modal"]'

    name = OUIATextInput('acs-edit-name-field')
    description = TextInput(locator='.//textarea[@id="acs_description_field"]')

    edit_button = OUIAButton('edit-acs-details-submit')
    cancel_button = OUIAButton('edit-acs-details-cancel')


class DualListSelector(EditModal):
    """Class representing some elements of the Dual List Selector modal."""

    available_options_search = SearchInput(
        locator='.//input[@aria-label="Available search input"]'
    )
    available_options_list = ItemsList(
        locator='.//div[contains(@class, "pf-m-available")]'
        '//ul[@class="pf-c-dual-list-selector__list"]'
    )

    add_selected = Button(locator='.//button[@aria-label="Add selected"]')
    add_all = Button(locator='.//button[@aria-label="Add all"]')
    remove_all = Button(locator='.//button[@aria-label="Remove all"]')
    remove_selected = Button(locator='.//button[@aria-label="Remove selected"]')

    chosen_options_search = SearchInput(locator='.//input[@aria-label="Chosen search input"]')
    chosen_options_list = ItemsList(
        locator='.//div[contains(@class, "pf-m-chosen")]'
        '//ul[@class="pf-c-dual-list-selector__list"]'
    )


class EditCapsulesModal(DualListSelector):
    """Class representing the Edit Capsule modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-smart-proxies-modal"]'

    use_http_proxies = Switch(locator='.//label[@for="use-http-proxies-switch"]')

    edit_button = Button(locator='.//div[@class="pf-c-form__actions"]/button[1]')
    # TODO Remove line above and uncomment line below when BZ2213190 is fixed
    # edit_button = OUIAButton('edit-acs-smart-proxies-submit')
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
    select_ca_cert = FormSelect(locator='.//select[option[text()="Select a CA certificate"]]')
    # TODO Remove line above and uncomment line below when BZ2212812 is fixed
    # select_ca_cert = OUIAFormSelect('sslCAcert-select')

    manual_auth_radio_btn = Radio(id='manual_auth')
    username = OUIATextInput('acs-username-field')
    password = OUIATextInput('acs-password-field')

    content_credentials_radio_btn = Radio(id='content_credentials')
    ssl_client_cert = OUIAFormSelect('ssl-client-cert-select')
    ssl_client_key = FormSelect(locator='.//select[option[text()="Select a client key"]]')
    # TODO Remove line above and uncomment line below when BZ2212812 is fixed
    # ssl_client_key = OUIAFormSelect('ssl-client-key-select')

    none_auth_radio_btn = Radio(id='none')

    edit_button = Button(locator='.//div[@class="pf-c-form__actions"]/button[1]')
    # TODO Remove line above and uncomment line below when BZ2212740 is fixed
    # edit_button = OUIAButton('edit-acs-credentials-submit')
    cancel_button = Button(locator='.//div[@class="pf-c-form__actions"]/button[2]')
    # TODO Remove line above and uncomment line below when BZ2212740 is fixed
    # cancel_button = OUIAButton('edit-acs-credentials-cancel')


class EditProductsModal(DualListSelector):
    """Class representing the Edit Products modal."""

    ROOT = '//div[@data-ouia-component-id="acs-edit-products-modal"]'

    edit_button = Button(locator='.//div[@class="pf-c-form__actions"]/button[1]')
    # TODO Remove line above and uncomment line below when BZ2213486 is fixed
    # edit_button = OUIAButton('edit-acs-credentials-submit')
    cancel_button = Button(locator='.//div[@class="pf-c-form__actions"]/button[2]')
    # TODO Remove line above and uncomment line below when BZ2213486 is fixed
    # cancel_button = OUIAButton('edit-acs-credentials-cancel')


class AddAlternateContentSourceModal(View):
    """
    Class representing the "Add Alternate Content Source" modal.
    It contains multiple nested classes each representing a step of the wizard.

    There are two variations of wizard steps depending on selected source type:

    * Select source type
    * Name source
    * Select Capsule
    - Simplified:
        * Select products
    - Custom, RHUI:
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
            './/button[contains(.,"Select smart proxy") or contains(.,"Select capsule")]'
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
    last_refresh = Text('//dd[contains(@aria-label, "name_text_value")]')
    # TODO Remove line above and uncomment line below when BZ2209938 is fixed
    # last_refresh = Text('//dd[contains(@aria-label, "last_refresh_text_value")]')

    @View.nested
    class details_stack_item(View, AcsStackItem):
        """Class representing the Details stack item in the ACS drawer."""

        ROOT = (
            '//div[normalize-space(.)="Details" and contains(@class, "pf-c-expandable-section")]'
        )

        title = OUIAText('expandable-details-text')
        edit_details = Button(
            locator='//button[contains(@aria-label, "edit-details-pencil-edit")]'
        )

        @View.nested
        class details_stack_content(View):
            """Class representing content of the Details stack item."""

            ROOT = '//div[@id="showDetails"]'

            name = Text('.//dd[@aria-label="name_text_value"][1]')
            # TODO Remove line above and uncomment line below when BZ2208161 & BZ2209938 are fixed
            # name = Text('.//dd[@aria-label="name_text_value"]')
            description = Text('//dd[@aria-label="description_text_value"]')
            type = Text('//dd[@aria-label="type_text_value"]')
            content_type = Text('//dd[@aria-label="content_type_text_value"]')

    @View.nested
    class capsules_stack_item(View, AcsStackItem):
        """Class representing the Capsules stack item in the ACS drawer"""

        # TODO Remove "Smart proxies" part from xpath after BZ2213768 is resolved"
        ROOT = (
            '//div[(normalize-space(.)="Smart proxies" or normalize-space(.)="Capsules")'
            ' and contains(@class, "pf-c-expandable-section")]'
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
    class url_and_subpaths_stack_item(View, AcsStackItem):
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
    class credentials_stack_item(View, AcsStackItem):
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
    class products_stack_item(View, AcsStackItem):
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

    def read(self):
        """Reads the ACS drawer and returns its content as a dictionary."""

        keys = ['details', 'capsules', 'url_and_subpaths', 'credentials', 'products']
        result = dict.fromkeys(keys)
        # Sleep ensures that all stack items are loaded and test does not fail
        time.sleep(3)
        # Expand and read each stack item
        for key in result:
            if key == 'details':
                self.details_stack_item.expand()
                result[key] = self.details_stack_item.read()
                result['details']['last_refresh'] = self.last_refresh.text
            elif key == 'capsules':
                self.capsules_stack_item.expand()
                result[key] = self.capsules_stack_item.read()
            elif key == 'url_and_subpaths':
                if self.url_and_subpaths_stack_item.is_displayed:
                    self.url_and_subpaths_stack_item.expand()
                    result[key] = self.url_and_subpaths_stack_item.read()
            elif key == 'credentials':
                if self.credentials_stack_item.is_displayed:
                    self.credentials_stack_item.expand()
                    result[key] = self.credentials_stack_item.read()
            elif key == 'products':
                if self.products_stack_item.is_displayed:
                    self.products_stack_item.expand()
                    result[key] = self.products_stack_item.read()

        # Remove None values from the result dictionary and return it
        result = {k: v for k, v in result.items() if v is not None}
        return result


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
        pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
