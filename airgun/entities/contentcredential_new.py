from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.contentcredential_new import ContentCredentialsNewTableView


class NewContentCredentialEntity(BaseEntity):
    """Entity for the React-based Content Credentials list page."""

    endpoint_path = '/labs/content_credentials'

    def search(self, value):
        """Search for content credentials in the table."""
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        return view.search(value)

    def read_table(self):
        """Read all rows from the content credentials table."""
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        return view.table.read()


@navigator.register(NewContentCredentialEntity, 'All')
class ShowAllNewContentCredentials(NavigateStep):
    """Navigate to the React-based Content Credentials list page."""

    VIEW = ContentCredentialsNewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Credentials')
