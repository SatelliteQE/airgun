from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.product import (
    ProductAdvancedSync,
    ProductCreateView,
    ProductEditView,
    ProductManageHttpProxy,
    ProductRepoDiscoveryView,
    ProductsTableView,
    ProductSyncPlanView,
    ProductTaskDetailsView,
    ProductVerifyContentChecksum,
)
from airgun.views.task import TaskDetailsView


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
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific product"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for already created product"""
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

    def manage_http_proxy(self, entities_list, values):
        """Manage HTTP proxy for product/products

        :param entities_list: The product names to perform Manage HTTP proxy action.
        :param values: dict containing http_proxy_policy and http_proxy values.
            eg: {'http_proxy_policy': 'No HTTP Proxy'}, {'http_proxy_policy': 'Global Default'},
            {'http_proxy_policy': 'Use specific HTTP Proxy', 'http_proxy': 'proxy_name'}
        """
        view = self.navigate_to(
            self,
            'Select Action',
            action_name='Manage HTTP proxy',
            entities_list=entities_list,
        )
        if values['http_proxy_policy'] == "Global Default":
            values['http_proxy_policy'] = view.http_proxy_policy.all_options[0][0]
        view.fill(values)
        view.update.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def advanced_sync(self, entities_list, sync_type):
        """Advanced Sync for product/products

        :param entities_list: The product names to perform Advanced Sync action.
        :param sync_type: value containing sync type.
            eg: sync_type="optimized", sync_type="complete"
        """

        view = self.navigate_to(
            self,
            'Select Action',
            action_name='Advanced Sync',
            entities_list=entities_list,
        )
        if sync_type == "optimized":
            view.optimized.click()
        elif sync_type == "complete":
            view.complete.click()
        view.sync.click()
        view.task.click()
        view = TaskDetailsView(view.browser)
        view.wait_for_result()
        return view.read()

    def verify_content_checksum(self, entities_list):
        """Verify Content Checksum for product/products

        :param entities_list: The product names to perform Verify Content Checksum action.
        """
        view = self.navigate_to(
            self,
            'Select Action',
            action_name='Verify Content Checksum',
            entities_list=entities_list,
        )
        view.task_alert.click()
        view = TaskDetailsView(view.browser)
        view.wait_for_result()
        return view.read()


@navigator.register(ProductEntity, 'All')
class ShowAllProducts(NavigateStep):
    """Navigate to the page that contains all Products"""

    VIEW = ProductsTableView

    @retry_navigation
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
        'Manage HTTP proxy': ProductManageHttpProxy,
        'Advanced Sync': ProductAdvancedSync,
        'Verify Content Checksum': ProductVerifyContentChecksum,
    }

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        action_name = kwargs.get('action_name')
        self.VIEW = self.ACTIONS_VIEWS.get(action_name)
        if not self.VIEW:
            raise ValueError(
                f'Please provide a valid action name. action_name: "{action_name}" not found.'
            )
        entities_list = kwargs.get('entities_list')
        for entity in entities_list:
            self.parent.table.row(name=entity)[0].click()
            if not self.parent.table.row(name=entity)[0].read():
                script = "document.getElementsByTagName('input')[2].click();"
                self.parent.browser.execute_script(script)
        self.parent.actions.fill(action_name)
