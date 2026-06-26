from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.exceptions import DisabledWidgetError
from airgun.navigation import NavigateStepWithWait as NavigateStep, navigator
from airgun.views.common import TableRowKebabMenu
from airgun.views.contentcredential import (
    ContentCredentialEditView,
    ContentCredentialsTableView,
    CreateContentCredentialModal,
    DeleteContentCredentialModal,
)
from airgun.views.product import ProductEditView


class ContentCredentialEntity(BaseEntity):
    # TODO: Update to '/content_credentials' once the React page is moved out of /labs
    endpoint_path = '/labs/content_credentials'

    def create(self, values):
        """Create new content credentials entity via modal.

        Args:
            values (dict): Should contain:
                - name (str): Name of the credential
                - content_type (str): Type - 'GPG Key' or 'Certificate'
                - content (str): The GPG key or certificate content

        Raises:
            DisabledWidgetError: If the create button is disabled due to missing required fields
        """
        view = self.navigate_to(self, 'All')
        view.create_button.click()
        modal = CreateContentCredentialModal(self.browser)
        modal.wait_displayed()
        modal.fill(
            {
                'name_input': values.get('name', ''),
                'content_type': values.get('content_type', ''),
                'content_text_box': values.get('content', ''),
            }
        )
        if modal.create_button.disabled:
            raise DisabledWidgetError(
                'Create button is disabled. Required fields (name and content) must be filled.'
            )
        modal.create_button.click()
        wait_for(
            lambda: not modal.is_displayed,
            timeout=30,
            delay=0.5,
            handle_exception=True,
            message='Waiting for create modal to close',
        )
        wait_for(
            lambda: view.table.row(name=values['name']),
            timeout=30,
            delay=0.5,
            handle_exception=True,
            message=f'Waiting for credential "{values["name"]}" to appear in table',
        )

    def delete(self, entity_name):
        """Delete existing content credentials entity via table row kebab menu."""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        wait_for(
            lambda: view.table.row(name=entity_name),
            timeout=30,
            delay=0.5,
            handle_exception=True,
            message=f'Waiting for credential "{entity_name}" row to appear',
        )
        TableRowKebabMenu(parent=view.table.row(name=entity_name)).item_select('Delete')
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
