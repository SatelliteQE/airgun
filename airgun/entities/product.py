from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.product import (
    ProductCreateView,
    ProductEditView,
    ProductRepoDiscoveryView,
    ProductTaskDetailsView,
    ProductsTableView,
    ProductSyncPlanView,
)


class ProductEntity(BaseEntity):
    endpoint_path = '/products'

    def create(self, values, sync_plan_values=None):
        """Creates new product from UI.

        :param sync_plan_values: dict with values for creating sync_plan from
         product create page
        """
        view = self.navigate_to(self, 'New')
        view.fill(values)
        if sync_plan_values:
            view.create_sync_plan.click()
            sync_plan_create_view = ProductSyncPlanView(self.browser)
            sync_plan_create_view.fill(sync_plan_values)
            sync_plan_create_view.submit.click()
            view.flash.assert_no_error()
            view.flash.dismiss()
        view.submit.click()

    def delete(self, entity_name):
        """Deletes product from UI"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove Product')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific product"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for already created product """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

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
