import time

from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.contentview_new import NewContentViewCreateView
# from airgun.views.contentview_new import NewContentViewDeleteView
from airgun.views.contentview_new import NewContentViewEditView
from airgun.views.contentview_new import NewContentViewTableView
from airgun.views.contentview_new import NewContentViewVersionPromote
from airgun.views.contentview_new import NewContentViewVersionPublishView


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
        """Publishes to create new version of CV and promotes the contents to
        'Library' environment.
        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        view.next.click()
        view.finish.click()
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.versions.table.read()

    def promote(self, entity_name, version_name, lce_name):
        """Promotes the selected version of content view to given environment.
        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Promote', entity_name=entity_name, version_name=version_name)
        modal = NewContentViewVersionPromote(self.browser)
        if modal.is_displayed:
            modal.lce.fill({lce_name: True})
            modal.promote.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.search(version_name)
        return view.versions.table.row(version=version_name).read()

    def publish_and_promote(self, entity_name, lce_name, values=None):
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        view.lce(lce_name).fill(True)
        view.next.click()
        view.next.click()
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.versions.table.read()

    def update(self, entity_name, values):
        """Update existing content view"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        # need a wait to recognize the loading is complete
        # sleep works for now
        time.sleep(3)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values


@navigator.register(NewContentViewEntity, 'All')
class ShowAllContentViewsScreen(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = NewContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle', 'Content Views')


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


@navigator.register(NewContentViewEntity, 'New')
class CreateContentView(NavigateStep):
    """Navigate to Create content view."""

    VIEW = NewContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_content_view.click()


@navigator.register(NewContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen.
    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewVersionPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        """Click 'Publish new version' button"""
        self.parent.publish.click()


@navigator.register(NewContentViewEntity, 'Promote')
class PromoteContentViewVersion(NavigateStep):
    """Navigate to Content View Promote screen.
    Args:
        entity_name: name of content view
        version_name: name of content view version to promote
    """

    VIEW = NewContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        version_name = kwargs.get('version_name')
        self.parent.versions.search(version_name)
        self.parent.versions.table[0][7].widget.item_select('Promote')
