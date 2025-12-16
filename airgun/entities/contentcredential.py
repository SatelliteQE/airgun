from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentcredential import (
    ContentCredentialCreateView,
    ContentCredentialEditView,
    ContentCredentialsTableView,
)
from airgun.views.product import ProductEditView


class ContentCredentialEntity(BaseEntity):
    endpoint_path = '/content_credentials'

    def create(self, values):
        """Create new content credentials entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete existing content credentials entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.remove.click()
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """search for content credentials entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read content credentials entity values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update content credentials entity values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def get_product_details(self, entity_name, product_name):
        """Get entity values for a product which associated to gpg key

        :param entity_name: Gpg key name
        :param product_name: Name of associated product
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.products.search(product_name)
        view.products.table.row(name=product_name)['Name'].widget.click()
        product_view = ProductEditView(self.browser)
        return product_view.read()


@navigator.register(ContentCredentialEntity, 'All')
class ShowAllContentCredentials(NavigateStep):
    """Navigate to All Content Credentials page"""

    VIEW = ContentCredentialsTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Credentials')


@navigator.register(ContentCredentialEntity, 'New')
class AddNewContentCredential(NavigateStep):
    """Navigate to Create Content Credential page"""

    VIEW = ContentCredentialCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ContentCredentialEntity, 'Edit')
class EditContentCredential(NavigateStep):
    """Navigate to Content Credential details screen.

    Args:
        entity_name: name of content credential to edit
    """

    VIEW = ContentCredentialEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
