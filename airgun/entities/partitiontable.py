from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.partitiontable import (
    PartitionTableEditView,
    PartitionTablesView,
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

    def update(self, values, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def clone(self, values, entity_name):
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def lock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Lock')

    def unlock(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Unlock')
        self.browser.handle_alert()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()


@navigator.register(PartitionTableEntity, 'All')
class ShowAllPartitionTables(NavigateStep):
    VIEW = PartitionTablesView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Hosts', 'Partition Tables')


@navigator.register(PartitionTableEntity, 'New')
class AddNewPartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(PartitionTableEntity, 'Edit')
class EditPartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(PartitionTableEntity, 'Clone')
class ClonePartitionTable(NavigateStep):
    VIEW = PartitionTableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
