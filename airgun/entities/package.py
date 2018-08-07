
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator

from airgun.views.package import PackagesView, PackageDetailsView


class PackageEntity(BaseEntity):
    """Package entity"""

    def search(self, query, repository='All Repositories', applicable=False,
               upgradable=False):
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
            query,
            repository=repository,
            applicable=applicable,
            upgradable=upgradable
        )

    def read(self, entity_name, repository='All Repositories'):
        """Read package values from Package Details page

        :param str entity_name: the package name to read.
        :param str repository: repository name to select when searching for the
            package.
        """
        view = self.navigate_to(
            self, 'Details', entity_name=entity_name, repository=repository)
        return view.read()


@navigator.register(PackageEntity, 'All')
class ShowAllPackages(NavigateStep):
    """navigate to Packages Page"""
    VIEW = PackagesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Packages')


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
        self.parent.search(
            'name = {0}'.format(entity_name), repository=repository)
        self.parent.table.row(
            ('RPM', 'startswith', entity_name))['RPM'].widget.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.view.package_name = entity_name
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[1].startswith(entity_name)
        )
