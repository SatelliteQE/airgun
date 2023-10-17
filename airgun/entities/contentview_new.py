from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.contentview_new import (
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewTableView,
    ContentViewVersionPublishView,
)


class NewContentViewEntity(BaseEntity):
    endpoint_path = '/content_views'

    def create(self, values):
        """Create a new content view"""
        view = self.navigate_to(self, 'New')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.search(value)

    def publish(self, entity_name, values=None):
        """Publishes new version of CV"""
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        if values:
            view.fill(values)
        view.next.click()
        view.finish.click()
        view.progressbar.wait_for_result(delay=0.01)
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.versions.table.wait_displayed()
        return view.versions.table.read()


@navigator.register(NewContentViewEntity, 'All')
class ShowAllContentViewsScreen(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = ContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle', 'Content Views')


@navigator.register(NewContentViewEntity, 'New')
class CreateContentView(NavigateStep):
    """Navigate to Create content view."""

    VIEW = ContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_content_view.click()


@navigator.register(NewContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View screen."""

    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen."""

    VIEW = ContentViewVersionPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    @retry_navigation
    def step(self, *args, **kwargs):
        """Click 'Publish new version' button"""
        self.parent.publish.click()
