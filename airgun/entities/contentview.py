from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentview import (
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewTableView,
    ContentViewVersionPromoteView,
    ContentViewVersionPublishView,
)


class ContentViewEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove Content View')
        view.dialog.confirm()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def add_yum_repo(self, entity_name, repo_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.yumrepo.repos.add(repo_name)

    def publish(self, entity_name, values=None):
        """Publishes to create new version of CV and promotes the contents to
        'Library' environment.

        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        view.save.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.resources[0]['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.resources[0].read()

    def promote(self, entity_name, version_name, lce_name):
        """Promotes the selected version of content view to given environment.

        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(
            self, 'Promote',
            entity_name=entity_name,
            version_name=version_name,
        )
        view.lce(lce_name).fill(True)
        view.promote.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.resources[0]['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.resources.row(version=version_name).read()


@navigator.register(ContentViewEntity, 'All')
class ShowAllContentViews(NavigateStep):
    VIEW = ContentViewTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Views')


@navigator.register(ContentViewEntity, 'New')
class AddNewContentView(NavigateStep):
    VIEW = ContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()


@navigator.register(ContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen.

    Args:
        entity_name: name of content view
    """
    VIEW = ContentViewVersionPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        """Dismiss alerts if present to uncover 'Publish' button, then click
        it.
        """
        self.parent.flash.dismiss()
        self.parent.publish.click()


@navigator.register(ContentViewEntity, 'Promote')
class PromoteContentViewVersion(NavigateStep):
    """Navigate to Content View Promote screen.

    Args:
        entity_name: name of content view
        version_name: name of content view version to promote
    """
    VIEW = ContentViewVersionPromoteView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        self.parent.versions.search(kwargs.get('version_name'))
        self.parent.versions.resources[0]['Actions'].fill('Promote')
