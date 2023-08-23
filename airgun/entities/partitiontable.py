from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.partitiontable import (
    PartitionTableCreateView,
    PartitionTableEditView,
    PartitionTablesView,
)


class PartitionTableEntity(BaseEntity):
    endpoint_path = '/templates/ptables'

    def create(
        self,
        values,
    ):
        """Create new partition table entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Read all values for created partition table entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def search(self, value):
        """Search for partition table entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def update(self, entity_name, values):
        """Update partition table entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def clone(self, entity_name, values):
        """Clone existing partition table entity"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def lock(self, entity_name):
        """Lock partition table entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Lock')
        view.flash.assert_no_error()
        view.flash.dismiss()

    def unlock(self, entity_name):
        """Unlock partition table entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Unlock')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing partition table"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(PartitionTableEntity, 'All')
class ShowAllPartitionTables(NavigateStep):
    """Navigate to All Partition Tables page"""

    VIEW = PartitionTablesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Templates', 'Partition Tables')


@navigator.register(PartitionTableEntity, 'New')
class AddNewPartitionTable(NavigateStep):
    """Navigate to Create Partition Table page"""

    VIEW = PartitionTableCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(PartitionTableEntity, 'Edit')
class EditPartitionTable(NavigateStep):
    """Navigate to Edit Partition Table page

    Args:
        entity_name: name of the partition table
    """

    VIEW = PartitionTableEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(PartitionTableEntity, 'Clone')
class ClonePartitionTable(NavigateStep):
    """Navigate to Create Partition Table page for cloned entity

    Args:
        entity_name: name of the partition table to be cloned
    """

    VIEW = PartitionTableCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
