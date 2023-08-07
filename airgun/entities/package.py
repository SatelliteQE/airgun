from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.package import PackageDetailsView
from airgun.views.package import PackagesView


class PackageEntity(BaseEntity):
    endpoint_path = '/packages'

    def search(self, query, repository='All Repositories', applicable=False, upgradable=False):
        """Search for package in the indicated repository

        :param str query: search query to type into search field. E.g.
            ``name = "bar"``.
        :param str repository: repository name to select when searching for the
            package.
        :param bool applicable: To show only applicable packages.
        :param bool upgradable: To show only upgradable packages.
        """
        view = self.navigate_to(self, 'All')
        return view.search(
            query, repository=repository, applicable=applicable, upgradable=upgradable
        )

    def read(self, entity_name, repository='All Repositories', widget_names=None):
        """Read package values from Package Details page

        :param str entity_name: the package name to read.
        :param str repository: repository name to select when searching for the
            package.
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name, repository=repository)
        return view.read(widget_names=widget_names)


@navigator.register(PackageEntity, 'All')
class ShowAllPackages(NavigateStep):
    """navigate to Packages Page"""

    VIEW = PackagesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Types', 'Packages')


@navigator.register(PackageEntity, 'Details')
class ShowPackageDetails(NavigateStep):
    """Navigate to Package Details page by clicking on necessary package name
    in the table

    Args:
        entity_name: The package name.
        repository: The package repository name.
    """

    VIEW = PackageDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        repository = kwargs.get('repository', 'All Repositories')
        self.parent.search(f'name = {entity_name}', repository=repository)
        self.parent.table.row(('RPM', 'startswith', entity_name))['RPM'].widget.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.view.package_name = entity_name
        return self.view.is_displayed and self.view.breadcrumb.locations[1].startswith(entity_name)
