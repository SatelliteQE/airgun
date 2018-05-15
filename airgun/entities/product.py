from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.product import (
    ProductCreateView,
    ProductEditView,
    ProductRepoDiscoveryView,
    ProductsTableView,
)


class ProductEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove Product')
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

    def discover_repo(self, values):
        view = self.navigate_to(self, 'Discovery')
        view.fill(values)
        view.create_repo.run_procedure.click()
        view.create_repo.wait_repo_created()


@navigator.register(ProductEntity, 'All')
class ShowAllProducts(NavigateStep):
    VIEW = ProductsTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Products')


@navigator.register(ProductEntity, 'New')
class AddNewProduct(NavigateStep):
    VIEW = ProductCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ProductEntity, 'Edit')
class EditProduct(NavigateStep):
    VIEW = ProductEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()


@navigator.register(ProductEntity, 'Discovery')
class ProductRepoDiscovery(NavigateStep):
    VIEW = ProductRepoDiscoveryView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.repo_discovery.click()
