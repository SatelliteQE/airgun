from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.partitiontable import (
    PartitionTableEditView,
    PartitionTableView,
)


class PartitionTableEntity(BaseEntity):

    def create(self, values,):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def clone(self, values, entity_name):
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def lock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.actions.fill('Lock')

    def unlock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.actions.fill('Unlock')
        self.browser.handle_alert()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.actions.fill('Delete')
        self.browser.handle_alert()


@navigator.register(PartitionTableEntity, 'All')
class ShowAllPartitionTables(NavigateStep):
    VIEW = PartitionTableView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Hosts', 'Partition Tables')


@navigator.register(PartitionTableEntity, 'New')
class AddNewPartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(PartitionTableEntity, 'Edit')
class EditPartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()


@navigator.register(PartitionTableEntity, 'Clone')
class ClonePartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.actions.fill('Clone')
