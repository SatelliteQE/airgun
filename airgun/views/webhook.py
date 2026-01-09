from wait_for import wait_for
from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import Button
from widgetastic_patternfly5 import Button as PF5Button, Tab

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import AutoCompleteTextInput, SatTable


class WebhooksView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Webhooks']")
    new = PF5Button('Create new')
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('//span[@type="button"]'),
            'Actions': Button('Delete'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class WebhookCreateView(BaseLoggedInView):
    ROOT = '//div[@id="webhookCreateModal"]'
    cancel_button = Button('Cancel')
    submit_button = Button('contains', 'Submit')

    @View.nested
    class general(Tab):
        subscribe_to = AutoCompleteTextInput(locator=("//div[@id='typeahead-select-input-event']"))
        name = TextInput(id='name')
        target_url = TextInput(id='id-target_url')
        template = AutoCompleteTextInput(
            locator=("//div[@id='typeahead-select-input-webhook_template_id']")
        )
        http_method = AutoCompleteTextInput(
            locator=("//div[@id='typeahead-select-input-http_method']")
        )
        enabled = Checkbox(id='id-enabled')

    @View.nested
    class credentials(Tab):
        user = TextInput(id='id-user')
        password = TextInput(id='id-password')
        verify_ssl = Checkbox(id='id-verify_ssl')
        capsule_auth = Checkbox(id='id-proxy_authorization')
        certs = TextInput(id='id-ssl_ca_certs')

    @View.nested
    class additional(Tab):
        content_type = TextInput(id='id-http_content_type')
        headers = TextInput(id='id-http_headers')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            locator=self.cancel_button, visible=True, exception=True
        ) is not None and 'in' in self.browser.classes(self)

    def wait_for_popup(self):
        is_popup_visible = self.browser.wait_for_element(
            self.cancel_button, visible=True, exception=False
        ) is not None and 'in' in self.browser.classes(self)
        are_fields_visible = self.browser.wait_for_element(
            self.general.subscribe_to, visible=True, exception=False
        )
        return is_popup_visible and are_fields_visible


class WebhookEditView(WebhookCreateView):
    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.cancel_button, visible=True, exception=False
        ) is not None and 'in' in self.browser.classes(self)


class DeleteWebhookConfirmationView(BaseLoggedInView):
    ROOT = (
        '//div[@role="dialog" and @tabindex]'
        '[div//h4[normalize-space(.)="Confirm Webhook Deletion"]]'
    )
    delete_button = Button('contains', 'Delete')
    cancel_button = Button('Cancel')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.delete_button, visible=True, exception=False
        ) is not None and 'in' in self.browser.classes(self)

    def wait_animation_end(self):
        wait_for(
            lambda: 'in' in self.browser.classes(self),
            handle_exception=True,
            logger=self.logger,
            timeout=10,
        )
