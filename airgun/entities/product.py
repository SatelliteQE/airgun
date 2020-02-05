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
    ProductManageHttpProxy,
    ProductSyncSelected
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

    def _select_action(self, action_name, entities_list, values=None):
        """Navigate to all entities, select the entities, and returns the view
        of the selected action name from main entity select action dropdown.
        """
        return self.navigate_to(
            self,
            'Select Action',
            action_name=action_name,
            entities_list=entities_list,
            values=values
        )

    def apply_action(self, action_name, entities_list, values=None):
        """Apply action name for product/products"""
        view = self._select_action(action_name, entities_list, values=None)
        if values['http_proxy_policy'] == "Global Default":
            values['http_proxy_policy'] = view.http_proxy_policy.all_options[0][0]
        view.fill(values)
        view.update.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def manage_http_proxy(self, entities_list, values):
        """Manage HTTP Proxy for product/products

        :param entities_list: The product names to perform Manage HTTP Proxy action.
        :param values: dict containing http_proxy_policy and http_proxy values.
            eg: {'http_proxy_policy': 'No HTTP Proxy'}, {'http_proxy_policy': 'Global Default'},
            {'http_proxy_policy': 'Use specific HTTP Proxy', 'http_proxy': 'proxy_name'}
        """
        view = self._select_action('Manage HTTP Proxy', entities_list, values=None)
        if values['http_proxy_policy'] == "Global Default":
            values['http_proxy_policy'] = view.http_proxy_policy.all_options[0][0]
        view.fill(values)
        view.update.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def sync_selected(self, entities_list):
        """Apply Sync Selected action on products listed in entities_list

        :param entities_list: The product names to perform sync operation.
        """
        view = self._select_action('Sync Selected', entities_list)
        view.flash.assert_no_error()
        view.flash.dismiss()


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


@navigator.register(ProductEntity, 'Select Action')
class ProductsSelectAction(NavigateStep):
    """Navigate to Action page by selecting checkboxes for necessary Products and
     then clicking on the action name button in 'Select Action' dropdown.

    Args:
        action_name: the action name to select from dropdown button
        entities_list: list of Products that need to be modified
    """
    ACTIONS_VIEWS = {
        'Manage HTTP Proxy': ProductManageHttpProxy,
        'Sync Selected': ProductSyncSelected,
    }

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        action_name = kwargs.get('action_name')
        self.VIEW = self.ACTIONS_VIEWS.get(action_name)
        if not self.VIEW:
            raise ValueError('Please provide a valid action name.'
                             ' action_name: "{0}" not found.')
        entities_list = kwargs.get('entities_list')
        if entities_list == "All":
            self.parent.select_all.click()
        else:
            for entity in entities_list:
                self.parent.table.row(name=entity)[0].click()
        self.parent.actions.fill(action_name)
