from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.contentview import (
    AddNewPuppetModuleView,
    ContentViewCopyView,
    ContentViewCreateView,
    ContentViewEditView,
    ContentViewRemoveView,
    ContentViewTableView,
    ContentViewVersionDetailsView,
    ContentViewVersionPromoteView,
    ContentViewVersionPublishView,
    ContentViewVersionRemoveConfirmationView,
    ContentViewVersionRemoveView,
    SelectPuppetModuleVersionView,
)


class ContentViewEntity(BaseEntity):

    def create(self, values):
        """Create a new content view"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete existing content view"""
        view = self.navigate_to(self, 'Delete', entity_name=entity_name)
        assert not view.conflicts_present, (
            'Unable to delete content view. '
            'Following conflicts are present: {}'.format(view.table.read())
        )
        view.remove.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def copy(self, entity_name, new_name):
        """Make a copy of existing content view"""
        view = self.navigate_to(self, 'Copy', entity_name=entity_name)
        view.new_name.fill(new_name)
        view.create.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read content view values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update existing content view"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def add_yum_repo(self, entity_name, repo_name):
        """Add YUM repository to content view"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.repositories.resources.add(repo_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

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

        :param str entity_name: content view name
        :param str module_name: puppet module name
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
        view.versions.searchbox.clear()
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
        view.versions.search(version_name)
        view.versions.table.row(
            version=version_name)['Status'].widget.wait_for_result()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return view.versions.table.row(version=version_name).read()

    def read_version(self, entity_name, version_name):
        """Read content view version values"""
        view = self.navigate_to(
            self, 'Version',
            entity_name=entity_name,
            version_name=version_name,
        )
        return view.read()

    def search_version(self, entity_name, query):
        """Search for content view version"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.versions.search(query)

    def search_version_package(
            self, entity_name, version_name, query, repo=None):
        """Search for a package inside content view version

        :param str entity_name: content view name
        :param str version_name: content view version name
        :param str query: search query for content view version's package
        :param str optional repo: repository name to filter by
        """
        view = self.navigate_to(
            self, 'Version',
            entity_name=entity_name,
            version_name=version_name,
        )
        return view.rpm_packages.search(query, repo=repo)

    def remove_version(self, entity_name, version_name, completely=True,
                       lces=None):
        """Remove content view version.

        :param str entity_name: content view name
        :param str version_name: content view version name
        :param bool completely: complete content view version removal if True
            or just disassociating from all lifecycle environments otherwise
        :param list optional lces: list of lifecycle environment names to
            select on content view version removal screen
        """
        view = self.navigate_to(
            self, 'Remove Version',
            entity_name=entity_name,
            version_name=version_name,
        )
        if lces:
            for row in view.table.rows():
                if 'ng-hide' in self.browser.classes(row):
                    # workaround for non-standard table with rows being present
                    # in DOM with 'ng-hide' class
                    continue
                row[0].widget.fill(row['Name'].text in lces)
        view.completely.fill(completely)
        view.next.click()
        view = ContentViewVersionRemoveConfirmationView(self.browser)
        view.confirm_remove.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.versions.search(version_name)
        view.versions.table.row(
            version=version_name)['Status'].widget.wait_for_result()


@navigator.register(ContentViewEntity, 'All')
class ShowAllContentViews(NavigateStep):
    """Navigate to All Content Views screen."""
    VIEW = ContentViewTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Views')


@navigator.register(ContentViewEntity, 'New')
class AddNewContentView(NavigateStep):
    """Navigate to New Content View screen."""
    VIEW = ContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View screen.

    Args:
        entity_name: name of content view
    """
    VIEW = ContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ContentViewEntity, 'Delete')
class DeleteContentView(NavigateStep):
    """Navigate to Delete Content View screen by selecting appropriate action
    on Edit Content View screen.

    Args:
        entity_name: name of content view
    """
    VIEW = ContentViewRemoveView

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.navigate_to(self.obj, 'Edit', entity_name=entity_name)

    def step(self, *args, **kwargs):
        self.parent.actions.fill('Remove Content View')


@navigator.register(ContentViewEntity, 'Copy')
class CopyContentView(NavigateStep):
    """Navigate to Copy Content View screen by selecting appropriate action in
    Content View Details screen.

    Args:
        entity_name: name of content view
    """
    VIEW = ContentViewCopyView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        self.parent.actions.fill('Copy Content View')


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


@navigator.register(ContentViewEntity, 'Version')
class ContentViewVersionDetails(NavigateStep):
    """Navigate to Content View Version details screen.

    Args:
        entity_name: name of content view
        version_name: name of content view version
    """
    VIEW = ContentViewVersionDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        version_name = kwargs.get('version_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[1] == entity_name
                and self.view.breadcrumb.locations[3] == version_name
        )

    def step(self, *args, **kwargs):
        version_name = kwargs.get('version_name')
        self.parent.versions.search(version_name)
        self.parent.versions.table.row(
            version=version_name)['Version'].widget.click()


@navigator.register(ContentViewEntity, 'Remove Version')
class RemoveContentViewVersion(NavigateStep):
    """Navigate to Content View Version removal screen by selecting
    corresponding action in content view versions table.

    Args:
        entity_name: name of content view
        version_name: name of content view version to remove
    """
    VIEW = ContentViewVersionRemoveView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(
            self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        version_name = kwargs.get('version_name')
        self.parent.versions.search(version_name)
        self.parent.versions.table.row(
            version=version_name)['Actions'].fill('Remove')
