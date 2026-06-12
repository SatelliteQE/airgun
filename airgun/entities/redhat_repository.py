from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStepWithWait as NavigateStep, navigator
from airgun.views.redhat_repository import RedHatRepositoriesView


class RedHatRepositoryEntity(BaseEntity):
    endpoint_path = '/redhat_repositories'

    def search(self, value, category='Available'):
        """Search RH repositories.

        :param str value: The value to search by.
        :param str category: The repository category to search, options: Available, Enabled, Both
        """
        view = self.navigate_to(self, 'All')
        return view.search(value, category=category)

    def read(self, entity_name=None, category='Available', recommended_repo=None, filter_type=None):
        """Read RH Repositories values.

        :param entity_name: The repository name
        :param category: The repository category to search, options: Available, Enabled
        :param recommended_repo: on/off RH recommended repositories
        :param filter_type: repository type such as RPM, Kickstart
        """
        view = self.navigate_to(self, 'All')

        if filter_type:
            view.filter_by_type.select(filter_type)

        if recommended_repo:
            view.recommended_repos.fill(recommended_repo == 'on')
            return view.available.read()

        entity_data = view.search(f'name = "{entity_name}"', category=category)[0]
        if category == 'Available':
            entity_data['items'] = view.available.items(name=entity_name)[0].read_items()
        return entity_data

    def enable(self, entity_name, arch, version=None, custom_query=None):
        """Enable a redhat repository.

        :param str entity_name: The RH repository set name.
        :param str arch: The system target repository architecture.
        :param str version: (optional) The OS release version if mandatory for this repository.
        :param str custom_query: (optional) The custom query to search for.
                    If custom_query is used, set entity_name to None when calling this function!!!
        """
        view = self.navigate_to(self, 'All')
        custom_query = f'name = "{entity_name}"' if custom_query is None else custom_query
        view.search(custom_query, category='Available')
        arch_version = f'{arch} {version}' if version else arch
        view.available.items(name=entity_name)[0].enable(arch_version)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def disable(self, entity_name, orphaned=False):
        """Disable a redhat repository.

        :param str entity_name: The RH repository name
        :param bool orphaned: Whether the repository is Orphaned
        """
        view = self.navigate_to(self, 'All')
        view.search(f'name = "{entity_name}"', category='Enabled')
        entity_text = f'{entity_name} (Orphaned)' if orphaned else entity_name
        view.enabled.items(name=entity_text)[0].disable()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(RedHatRepositoryEntity, 'All')
class ShowAllRepositories(NavigateStep):
    """Navigate to the page that contains Red Hat products repositories"""

    VIEW = RedHatRepositoriesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Red Hat Repositories')
