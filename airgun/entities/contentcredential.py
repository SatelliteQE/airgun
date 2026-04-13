from wait_for import wait_for

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

    def get_product_details(self, entity_name, product_name=None, filter=None):
        """Read products tab or navigate into a specific product's details.

        :param entity_name: Content credential name
        :param product_name: If given, click into that product and return its details page values
        :param filter: Optional string to filter the products table by name
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        if not view.products.table.is_displayed:
            return []
        if filter:
            view.products.filter_input.fill(filter)
        if product_name is None:
            return view.products.table.read()
        view.products.table.row(name=product_name)['Name'].widget.click()
        product_view = ProductEditView(self.browser)
        return product_view.read()

    def get_repository_details(self, entity_name, repository_name=None, filter=None):
        """Read repositories tab or navigate into a specific repository's details.

        :param entity_name: Content credential name
        :param repository_name: If given, click into that repository and return its details page values
        :param filter: Optional string to filter the repositories table by name
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        if not view.repositories.table.is_displayed:
            return []
        if filter:
            view.repositories.filter_input.fill(filter)
        if repository_name is None:
            return view.repositories.table.read()
        view.repositories.table.row(name=repository_name)['Name'].widget.click()
        return view.read()

    def get_acs_details(self, entity_name, acs_name=None, filter=None):
        """Read alternate content sources tab or navigate into a specific ACS's details.

        :param entity_name: Content credential name
        :param acs_name: If given, click into that ACS and return its details page values
        :param filter: Optional string to filter the ACS table by name
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        if not view.alternate_content_sources.table.is_displayed:
            return []
        if filter:
            view.alternate_content_sources.filter_input.fill(filter)
        if acs_name is None:
            return view.alternate_content_sources.table.read()
        view.alternate_content_sources.table.row(name=acs_name)['Name'].widget.click()
        return view.read()


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
        wait_for(
            lambda: self.parent.table.row(name=entity_name),
            timeout=30,
            delay=0.5,
            handle_exception=True,
            message=f'Waiting for content credential "{entity_name}" row to appear',
        )
        self.parent.table.row(name=entity_name)['Name'].widget.click()
