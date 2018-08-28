from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.syncplan import (
    SyncPlanCreateView,
    SyncPlanEditView,
    SyncPlansView,
)


class SyncPlanEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values


@navigator.register(SyncPlanEntity, 'All')
class ShowAllSyncPlans(NavigateStep):
    VIEW = SyncPlansView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Sync Plans')


@navigator.register(SyncPlanEntity, 'New')
class AddNewSyncPlan(NavigateStep):
    VIEW = SyncPlanCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(SyncPlanEntity, 'Edit')
class EditSyncPlan(NavigateStep):
    VIEW = SyncPlanEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
