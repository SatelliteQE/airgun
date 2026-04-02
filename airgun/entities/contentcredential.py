from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStepWithWait as NavigateStep, navigator
from airgun.views.contentcredential import (
    ContentCredentialCreateView,
    ContentCredentialEditView,
    ContentCredentialsTableView,
    DeleteContentCredentialModal,
)
from airgun.views.product import ProductEditView


class ContentCredentialEntity(BaseEntity):
    # TODO: Update to '/content_credentials' once the React page is moved out of /labs
    endpoint_path = '/labs/content_credentials'

    def create(self, values):
        """Create new content credentials entity."""
        raise NotImplementedError(
            'Content Credential create is not yet implemented in the React UI'
        )

    def delete(self, entity_name):
        """Delete existing content credentials entity via kebab menu."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.item_select('Delete')
        modal = DeleteContentCredentialModal(self.browser)
        modal.wait_displayed()
        modal.confirm_delete.click()

    def search(self, value):
        """Search for content credentials entity."""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read content credentials entity values."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update content credentials entity values."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def get_product_details(self, entity_name, product_name):
        """Get entity values for a product associated to this content credential.

        :param entity_name: Content credential name
        :param product_name: Name of associated product
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.products.table.row(name=product_name)['Name'].widget.click()
        product_view = ProductEditView(self.browser)
        return product_view.read()


@navigator.register(ContentCredentialEntity, 'All')
class ShowAllContentCredentials(NavigateStep):
    """Navigate to All Content Credentials page."""

    VIEW = ContentCredentialsTableView

    def step(self, *args, **kwargs):
        # TODO: Update menu path to 'Content', 'Content Credentials' once the page is moved out of /labs
        self.view.menu.select('Lab Features', 'Content Credentials')


@navigator.register(ContentCredentialEntity, 'New')
class AddNewContentCredential(NavigateStep):
    """Navigate to Create Content Credential page (stub)."""

    VIEW = ContentCredentialCreateView

    def step(self, *args, **kwargs):
        raise NotImplementedError(
            'Content Credential create is not yet implemented in the React UI'
        )


@navigator.register(ContentCredentialEntity, 'Edit')
class EditContentCredential(NavigateStep):
    """Navigate to Content Credential details screen.

    Args:
        entity_name: name of content credential to view/edit
    """

    VIEW = ContentCredentialEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
