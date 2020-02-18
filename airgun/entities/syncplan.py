from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.syncplan import SyncPlanCreateView
from airgun.views.syncplan import SyncPlanEditView
from airgun.views.syncplan import SyncPlansView


class SyncPlanEntity(BaseEntity):
    endpoint_path = '/sync_plans'

    def create(self, values):
        """Create new sync plan"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing sync plan"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for sync plan"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read values for created sync plan"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update sync plan with necessary values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def add_product(self, entity_name, products_list):
        """Add product to sync plan

        :param str entity_name: sync plan name
        :param products_list: either one or list of products
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.products.resources.add(products_list)
        assert view.flash.is_displayed
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(SyncPlanEntity, 'All')
class ShowAllSyncPlans(NavigateStep):
    """Navigate to All Sync Plans screen."""
    VIEW = SyncPlansView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Sync Plans')


@navigator.register(SyncPlanEntity, 'New')
class AddNewSyncPlan(NavigateStep):
    """Navigate to New Sync Plan screen."""
    VIEW = SyncPlanCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(SyncPlanEntity, 'Edit')
class EditSyncPlan(NavigateStep):
    """Navigate to Edit Sync Plan screen.

    Args:
        entity_name: name of sync plan
    """
    VIEW = SyncPlanEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
