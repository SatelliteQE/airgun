from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.contentview_new import NewContentViewCreateView
from airgun.views.contentview_new import NewContentViewEditView
from airgun.views.contentview_new import NewContentViewPublishView
from airgun.views.contentview_new import NewContentViewTableView

class NewContentViewEntity(BaseEntity):
    endpoint_path = '/content_views'

    def create(self, values):
        """Create a new content view"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def publish(self, entity_name, values=None):
        """Publishes to create new version of a CV and promotes the contents to
        a choosen environment.  Default is 'Library' if none is selected

        :return: dict with new content view version table row; contains keys
            like 'Version', 'Environments', 'Packages', etc.
        """
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        # goes right into the publish modal
        view.next.click()
        # land on review details in publish
        view.finish.click()
        # ensure that progressbar is done
        view.progressbar.is_completed()
        # navigate back to cv edit page and read the cvv table
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.table[0].widget.wait_for_result()
        return view.versions.table[0].read()

@navigator.register(NewContentViewEntity, 'All')
class ShowAllContentViewsScreen(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = NewContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Views')


@navigator.register(NewContentViewEntity, 'New')
class CreateContentView(NavigateStep):
    """Navigate to Create content view."""

    VIEW = NewContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_content_view.click()


@navigator.register(NewContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View screen.
    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen.
    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        """Click 'Publish new version' button"""
        wait_for(
            lambda: self.parent.publish.is_displayed,
            handle_exception=True,
            logger=self.view.logger,
            timeout=10,
        )
        self.parent.publish.click()