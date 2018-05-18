from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentview import (
    AddNewPuppetModuleView,
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewTableView,
    ContentViewVersionPromoteView,
    ContentViewVersionPublishView,
    SelectPuppetModuleVersionView,
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
        view.repositories.resources.add(repo_name)

    def add_cv(self, entity_name, cv_name):
        """Add content view to selected composite content view."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        assert view.content_views.is_displayed, (
            'Could not find "Content Views" tab. '
            'Make sure {} is composite content view'
            .format(entity_name)
        )
        view.content_views.resources.add(cv_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_puppet_module(self, entity_name, module_name, filter_term=None):
        """Add puppet module to selected view either by its author name or by
        its version.

        :param str optional filter_term: can be used to filter the module by
            'author' or by 'version'.
        """
        view = self.navigate_to(
            self, 'SelectPuppetModuleVersion',
            entity_name=entity_name,
            module_name=module_name
        )
        if filter_term:
            view.search(filter_term)
        view.table[0]['Actions'].widget.click()
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
        view.save.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
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
            self, 'Promote',
            entity_name=entity_name,
            version_name=version_name,
        )
        view.lce(lce_name).fill(True)
        view.promote.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.table[0]['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.table.row(version=version_name).read()


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
        self.parent.new.click()


@navigator.register(ContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ContentViewEntity, 'AddPuppetModule')
class AddNewPuppetModule(NavigateStep):
    """Navigate to Content View's "Add new Puppet Module" screen.

    Args:
        entity_name: name of content view
    """
    VIEW = AddNewPuppetModuleView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        self.parent.puppet_modules.add_new_module.click()


@navigator.register(ContentViewEntity, 'SelectPuppetModuleVersion')
class SelectPuppetModuleVersion(NavigateStep):
    """Navigate to new puppet module's "Select an Available Version" screen.

    Args:
        entity_name: name of content view
        module_name: name of puppet module
    """
    VIEW = SelectPuppetModuleVersionView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'AddPuppetModule', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        module_name = kwargs.get('module_name')
        self.parent.search(module_name)
        self.parent.table.row(name=module_name)['Actions'].widget.click()


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
        version_name = kwargs.get('version_name')
        self.parent.versions.search(version_name)
        self.parent.versions.table.row(
            version=version_name)['Actions'].fill('Promote')
