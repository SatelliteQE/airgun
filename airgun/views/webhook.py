from widgetastic.widget import Checkbox, Text, TextInput
from widgetastic_patternfly5 import Button as PF5Button
from widgetastic_patternfly5.ouia import Button as PF5OUIAButton

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import PF5TypeaheadSelect, SatTable


class WebhooksView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Webhooks']")
    new = PF5Button('Create new')
    table = SatTable(
        './/table',
        column_widgets={
            'Name': PF5OUIAButton('name-edit-active-button'),
            'Actions': PF5Button(locator='.//button[contains(@id, "delete")]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class WebhookFormView(BaseLoggedInView):
    """Base view for webhook create/edit forms."""

    cancel_button = PF5Button('Cancel')
    submit_button = PF5Button('Submit')

    # Tab buttons
    general_tab = PF5OUIAButton('webhook-form-tab-general')
    credentials_tab = PF5OUIAButton('webhook-form-tab-creds')
    additional_tab = PF5OUIAButton('webhook-form-tab-add')

    # General tab fields
    subscribe_to = PF5TypeaheadSelect(locator='//input[@id="id-event"]')
    name = TextInput(locator='//input[@id="id-name"]')
    target_url = TextInput(locator='//input[@id="id-target_url"]')
    template = PF5TypeaheadSelect(locator='//input[@id="id-webhook_template_id"]')
    http_method = PF5TypeaheadSelect(locator='//input[@id="id-http_method"]')
    enabled = Checkbox(id='id-enabled')

    # Credentials tab fields
    user = TextInput(locator='//input[@id="id-user"]')
    password = TextInput(locator='//input[@id="id-password"]')
    verify_ssl = Checkbox(id='id-verify_ssl')
    capsule_auth = Checkbox(id='id-proxy_authorization')
    certs = TextInput(locator='//textarea[@id="id-ssl_ca_certs"]')

    # Additional tab fields
    content_type = TextInput(locator='//input[@id="id-http_content_type"]')
    headers = TextInput(locator='//textarea[@id="id-http_headers"]')

    def _switch_to_tab(self, tab_name):
        """Click tab button to switch tabs."""
        tab_buttons = {
            'general': self.general_tab,
            'credentials': self.credentials_tab,
            'additional': self.additional_tab,
        }
        tab_buttons[tab_name].click()
        self.browser.plugin.ensure_page_safe()

    def fill(self, values):
        """Fill form values. Expects {'tab.field': value} format."""
        tabs_to_fill = {'general': {}, 'credentials': {}, 'additional': {}}
        for key, value in values.items():
            tab_name, field_name = key.split('.', 1)
            tabs_to_fill[tab_name][field_name] = value

        for tab_name in ['general', 'credentials', 'additional']:
            if tabs_to_fill[tab_name]:
                self._switch_to_tab(tab_name)
                for field_name, value in tabs_to_fill[tab_name].items():
                    getattr(self, field_name).fill(value)

    def read(self):
        """Read form values from all tabs."""
        result = {'general': {}, 'credentials': {}, 'additional': {}}
        fields = {
            'general': ['subscribe_to', 'name', 'target_url', 'template', 'http_method', 'enabled'],
            'credentials': ['user', 'password', 'verify_ssl', 'capsule_auth', 'certs'],
            'additional': ['content_type', 'headers'],
        }
        for tab_name, field_list in fields.items():
            self._switch_to_tab(tab_name)
            for field_name in field_list:
                widget = getattr(self, field_name)
                result[tab_name][field_name] = widget.read() if widget.is_displayed else None
        return result

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.cancel_button, visible=True, exception=False)
            is not None
        )

    def wait_for_popup(self):
        return (
            self.browser.wait_for_element(
                self.cancel_button, visible=True, timeout=30, exception=False
            )
            is not None
        )


class WebhookCreateView(WebhookFormView):
    ROOT = '//div[@id="webhookCreateModal"]'


class WebhookEditView(WebhookFormView):
    ROOT = '//div[@id="webhookEditModal"]'


class DeleteWebhookConfirmationView(BaseLoggedInView):
    ROOT = '//div[@id="webhookDeleteModal"]'
    delete_button = PF5Button('Delete')
    cancel_button = PF5Button('Cancel')

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.delete_button, visible=True, exception=False)
            is not None
        )

    def wait_animation_end(self):
        self.browser.wait_for_element(self.delete_button, visible=True, timeout=10)
