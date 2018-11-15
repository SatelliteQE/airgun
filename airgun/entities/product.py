from wait_for import wait_for
from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.product import (
    ProductCreateView,
    ProductEditView,
    ProductRepoDiscoveryView,
    ProductTaskDetailsView,
    ProductsTableView,
)


class ProductEntity(BaseEntity):

    def create(self, values):
        """Creates new product from UI"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Deletes product from UI"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove Product')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()
        view = self.navigate_to(self, 'All')
        wait_for(
            lambda: view.search('name = "{0}"'.format(entity_name)) == [],
            timeout=30,
            delay=2,
            logger=view.logger
        )

    def search(self, value):
        """Search for specific product"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read all values for already created product """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Updates product from UI"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def discover_repo(self, values):
        """Repo discovery procedure"""
        view = self.navigate_to(self, 'Discovery')
        view.fill(values)
        view.create_repo.run_procedure.click()
        view.create_repo.wait_repo_created()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def synchronize(self, entity_name):
        """Synchronize product"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Sync Now')
        view = ProductTaskDetailsView(view.browser)
        view.progressbar.wait_for_result()
        return view.read()


@navigator.register(ProductEntity, 'All')
class ShowAllProducts(NavigateStep):
    """Navigate to the page that contains all Products"""
    VIEW = ProductsTableView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Products')


@navigator.register(ProductEntity, 'New')
class AddNewProduct(NavigateStep):
    """Navigate to Create New Product page"""
    VIEW = ProductCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ProductEntity, 'Edit')
class EditProduct(NavigateStep):
    """Navigate to Edit Product page.

    Args:
        entity_name: name of the product to be updated
    """
    VIEW = ProductEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ProductEntity, 'Discovery')
class ProductRepoDiscovery(NavigateStep):
    """Navigate to Repo Discovery page for Product entity."""
    VIEW = ProductRepoDiscoveryView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.repo_discovery.click()
