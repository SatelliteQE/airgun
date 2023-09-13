from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.webhook import (
    DeleteWebhookConfirmationView,
    WebhookCreateView,
    WebhookEditView,
    WebhooksView,
)


class WebhookEntity(BaseEntity):
    endpoint_path = '/webhooks'

    def create(self, values):
        """Create new Webhook

        :param values: Parameters to be assigned to a Webhook,
            Name, Subscribe to, Target URL, Template and HTTP Method should be provided
        """
        view = self.navigate_to(self, 'New')
        view.wait_for_popup()
        view.fill(values)
        view.submit_button.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete corresponding Webhook

        :param str entity_name: name of the corresponding Webhook
        """
        view = self.navigate_to(self, 'Delete', entity_name=entity_name)
        view.wait_animation_end()
        view.delete_button.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, entity_name):
        """Search for a specific Webhook"""
        view = self.navigate_to(self, 'All')
        return view.search(entity_name)

    def read(self, entity_name, widget_names=None):
        """Reads content of corresponding Webhook

        :param str entity_name: name of the corresponding Webhook
        :return: dict representing tabs, with nested dicts representing fields
            and values
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.wait_for_popup()
        result = view.read(widget_names=widget_names)
        view.cancel_button.click()
        return result

    def update(self, entity_name, values):
        """Update existing Webhook

        :param str entity_name: name of the corresponding Webhook
        :param values: parameters to be changed at Webhook
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.wait_for_popup()
        view.fill(values)
        view.submit_button.click()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(WebhookEntity, 'All')
class ShowAllWebhooks(NavigateStep):
    """Navigate to All Webhooks screen."""

    VIEW = WebhooksView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Webhooks')


@navigator.register(WebhookEntity, 'New')
class AddNewWebhook(NavigateStep):
    """Navigate to Create Webhook page."""

    VIEW = WebhookCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(WebhookEntity, 'Edit')
class EditWebhook(NavigateStep):
    """Navigate to Edit Webhook page.

    Args:
        entity_name: name of the Webhook
    """

    VIEW = WebhookEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(WebhookEntity, 'Delete')
class DeleteWebhook(NavigateStep):
    """Search for Webhook and confirm deletion in dialog.

    Args:
        entity_name: name of the Webhook
    """

    VIEW = DeleteWebhookConfirmationView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.click()
