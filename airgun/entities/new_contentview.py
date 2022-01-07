import time
from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.new_contentview import NewContentViewCreateView
from airgun.views.new_contentview import NewContentViewEditView
from airgun.views.new_contentview import NewContentViewRemoveView
from airgun.views.new_contentview import NewContentViewTableView
from airgun.views.new_contentview import NewContentViewVersionPromoteView
from airgun.views.new_contentview import NewContentViewVersionPublishView

class NewContentViewEntity(BaseEntity):
    endpoint_path = '/content_views'

    def create(self, values, composite=False):
        """Create a new content view"""
        view = self.navigate_to(self, 'Create')
        if composite is True:
            view.composite.click()
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete existing content view"""
        view = self.navigate_to(self, 'Delete', entity_name=entity_name)
        assert (
            not view.conflicts_present
        ), f'Unable to delete content view. Following conflicts are present: {view.table.read()}'
        view.remove.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read content view values, optionally only the widgets in widget_names will be read."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def add_repo(self, entity_name, repo_name):
        """Add repository to content view"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        self.browser.wait_for_element(locator='//div[@class="pf-c-content"]')
        view.repositories.resources.add(repo_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def publish(self, entity_name, values=None):
        """Publishes to create new version of CV and promotes the contents to
        'Library' environment.

        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        # some type of breaks/pause needed in between to recognized current location before
        # proceeding to next screen
        view.next.click()
        view.next.click()
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        # TODO: Not able to recognize table very well
        view.versions.table[0]['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.table[0].read()

    def promote(self, entity_name, version_name, lce_name):
        """Promotes the selected version of content view to given environment.

        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(
            self,
            'Promote',
            entity_name=entity_name,
            version_name=version_name,
        )
        view.lce(lce_name).fill(True)
        view.promote.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.search(version_name)
        view.versions.table.row(version=version_name)['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.table.row(version=version_name).read()

    def publish_and_promote(self, entity_name, lce_name, values=None):
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        # some type of breaks/pause needed in between to recognized current location before
        # proceeding to next screen
        view.lce(lce_name).fill(True)
        view.next.click()
        view.next.click()
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        # TODO: Not able to recognize table very well
        view.versions.table[0]['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.table[0].read()


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
class ShowAllContentViews(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = NewContentViewTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Views')


@navigator.register(NewContentViewEntity, 'Create')
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

@navigator.register(NewContentViewEntity, 'Delete')
class DeleteContentView(NavigateStep):
    """Navigate to Delete Content View screen by selecting appropriate action
    on Edit Content View screen.

    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewRemoveView

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.navigate_to(self.obj, 'Edit', entity_name=entity_name)

    def step(self, *args, **kwargs):
        self.parent.actions.fill('Remove Content View')

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
        wait_for(
            lambda: self.parent.publish.is_displayed,
            handle_exception=True,
            logger=self.view.logger,
            timeout=10,
        )
        self.parent.publish.click()

@navigator.register(NewContentViewEntity, 'Promote')
class PromoteContentViewVersion(NavigateStep):
    """Navigate to Content View Promote screen.

    Args:
        entity_name: name of content view
        version_name: name of content view version to promote
    """

    VIEW = NewContentViewVersionPromoteView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        version_name = kwargs.get('version_name')
        self.parent.versions.search(version_name)
        self.parent.versions.table.row(version=version_name)['Actions'].fill('Promote')