from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.entities.product import ProductEntity
from airgun.entities.settings import SettingsEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.product import ProductTaskDetailsView
from airgun.views.repository import RepositoriesView
from airgun.views.repository import RepositoryCreateView
from airgun.views.repository import RepositoryEditView
from airgun.views.repository import RepositoryPackagesView
from airgun.views.repository import RepositoryPuppetModulesView


class RepositoryEntity(BaseEntity):
    def _find_default_http_proxy(self, values):
        """ Finds the global proxy name and returns updated values accordingly."""
        proxy = SettingsEntity(self.browser)
        result = proxy.read(property_name='name = content_default_http_proxy')['table'][0]['Value']
        global_proxy_name = result.split()[0]
        if global_proxy_name == 'no':
            global_proxy_name = 'None'
        values["repo_content.http_proxy_policy"] = f'Global Default ({global_proxy_name})'
        return values

    def create(self, product_name, values):
        """Create new repository for product"""
        if values.get("repo_content.http_proxy_policy") == "Global Default":
            values = self._find_default_http_proxy(values)
        view = self.navigate_to(self, 'New', product_name=product_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, product_name, value):
        """Search for specific product repository"""
        view = self.navigate_to(self, 'All', product_name=product_name)
        return view.search(value)

    def read(self, product_name, entity_name, widget_names=None):
        """Read values for repository"""
        view = self.navigate_to(self, 'Edit', product_name=product_name, entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, product_name, entity_name, values):
        """Update product repository values"""
        if values.get("repo_content.http_proxy_policy") == "Global Default":
            values = self._find_default_http_proxy(values)
        view = self.navigate_to(self, 'Edit', product_name=product_name, entity_name=entity_name)
        view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def upload_content(self, product_name, entity_name, file_name):
        """Upload a new content to existing repository"""
        view = self.navigate_to(self, 'Edit', product_name=product_name, entity_name=entity_name)
        view.repo_content.upload_content.fill(file_name)
        view.repo_content.upload.click()
        wait_for(
            lambda: view.flash.assert_message(
                f'Successfully uploaded content: {file_name.rpartition("/")[-1]}'
            ),
            handle_exception=True,
            timeout=120,
            logger=view.flash.logger,
        )
        view.flash.dismiss()

    def delete(self, product_name, entity_name):
        """Delete specific product repository"""
        view = self.navigate_to(self, 'All', product_name=product_name)
        view.search(entity_name)
        view.table.row(name=entity_name)[0].fill(True)
        view.delete.click()
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()
        wait_for(
            lambda: view.search(f'name = "{entity_name}"') == [],
            timeout=30,
            delay=2,
            logger=view.logger,
        )

    def synchronize(self, product_name, entity_name):
        """Synchronize repository"""
        view = self.navigate_to(self, 'Sync', product_name=product_name, entity_name=entity_name)
        view.progressbar.wait_for_result()
        return view.read()

    def remove_all_packages(self, product_name, entity_name):
        """Remove all packages from repository"""
        view = self.navigate_to(
            self,
            'Packages',
            product_name=product_name,
            entity_name=entity_name,
        )
        max_per_page = max([int(el.text) for el in view.items_per_page.all_options])
        view.items_per_page.fill(str(max_per_page))
        for _ in range(int(view.total_packages.text) // max_per_page + 1):
            view.select_all.fill(True)
            view.remove_packages.click()
            view.dialog.confirm()
            view.flash.assert_no_error()
            view.flash.dismiss()
        if view.total_packages.text != '0':
            raise AssertionError(f'Unable to remove all packages from {entity_name}')

    def remove_all_puppet_modules(self, product_name, entity_name):
        """Remove all puppet modules from repository"""
        view = self.navigate_to(
            self,
            'Puppet Modules',
            product_name=product_name,
            entity_name=entity_name,
        )
        max_per_page = max([int(el.text) for el in view.items_per_page.all_options])
        view.items_per_page.fill(str(max_per_page))
        for _ in range(int(view.total_puppet_modules.text) // max_per_page + 1):
            view.select_all.fill(True)
            view.remove_packages.click()
            view.dialog.confirm()
            view.flash.assert_no_error()
            view.flash.dismiss()
        if view.total_puppet_modules.text != '0':
            raise AssertionError(f'Unable to remove all puppet modules from {entity_name}')


@navigator.register(RepositoryEntity, 'All')
class ShowAllRepositories(NavigateStep):
    """Navigate to All Product Repositories page by pressing 'Repositories'
    Tab on Product Edit View page

    Args:
        product_name: name of product
    """

    VIEW = RepositoriesView

    def am_i_here(self, *args, **kwargs):
        product_name = kwargs.get('product_name')
        return self.view.is_displayed and self.view.breadcrumb.locations[1] == product_name

    def prerequisite(self, *args, **kwargs):
        product_name = kwargs.get('product_name')
        return self.navigate_to(ProductEntity, 'Edit', entity_name=product_name)

    def step(self, *args, **kwargs):
        self.parent.repositories.click()


@navigator.register(RepositoryEntity, 'New')
class AddNewRepository(NavigateStep):
    """Navigate to Create Product Repository page

    Args:
        product_name: name of product
    """

    VIEW = RepositoryCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(RepositoryEntity, 'Edit')
class EditRepository(NavigateStep):
    """Navigate to Edit Product Repository page

    Args:
        product_name: name of product
        entity_name: name of repository
    """

    VIEW = RepositoryEditView

    def am_i_here(self, *args, **kwargs):
        prod_name = kwargs.get('product_name')
        repo_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] == prod_name
            and self.view.breadcrumb.locations[3] == repo_name
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(RepositoryEntity, 'Sync')
class SyncRepository(NavigateStep):
    """Trigger repository synchronization and proceed to product task details
    page

    Args:
        product_name: name of product
        entity_name: name of repository
    """

    VIEW = ProductTaskDetailsView

    def am_i_here(self, *args, **kwargs):
        prod_name = kwargs.get('product_name')
        return self.view.is_displayed and self.view.breadcrumb.locations[1] == prod_name

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)[0].fill(True)
        self.parent.sync.click()


@navigator.register(RepositoryEntity, 'Packages')
class RepositoryPackages(NavigateStep):
    """Open repository details page and click 'Packages' link from 'Content
    Counts' table to proceed to Packages page.

    Args:
        product_name: name of product
        entity_name: name of repository
    """

    VIEW = RepositoryPackagesView

    def am_i_here(self, *args, **kwargs):
        prod_name = kwargs.get('product_name')
        repo_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] == prod_name
            and self.view.breadcrumb.locations[3] == repo_name
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.content_counts.row((0, 'Packages'))[1].widget.click()


@navigator.register(RepositoryEntity, 'Puppet Modules')
class RepositoryPuppetModules(NavigateStep):
    """Open repository details page and click 'Puppet Modules' link from
    'Content Counts' table to proceed to Puppet Modules page.

    Args:
        product_name: name of product
        entity_name: name of repository
    """

    VIEW = RepositoryPuppetModulesView

    def am_i_here(self, *args, **kwargs):
        prod_name = kwargs.get('product_name')
        repo_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[1] == prod_name
            and self.view.breadcrumb.locations[3] == repo_name
        )

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', **kwargs)

    def step(self, *args, **kwargs):
        self.parent.content_counts.row((0, 'Puppet Modules'))[1].widget.click()
