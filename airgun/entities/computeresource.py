from navmazing import NavigateToSibling
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeresource import (
    ComputeResourcesView,
    ResourceProviderEditView,
    ResourceProviderDetailView,
)


class ComputeResourceEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def edit(self, name, values):
        view = self.navigate_to(self, 'Edit', entity_name=name)
        view.fill(values)
        view.submit.click()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def delete(self, value):
        view = self.navigate_to(self, 'All')
        view.search(value)
        view.table.row(name=value)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def list_vms(self, rhev_name, expected_vm_name=None):
        """Returns all the VMs on the CR or VM with specified name"""
        view = self.navigate_to(self, 'Detail', rhev_name=rhev_name)
        return view.virtual_machines.table.row(name=expected_vm_name) if \
            expected_vm_name is not None else \
            view.virtual_machines.table.rows()

    def vm_status(self, rhev_name, vm_name):
        """Returns True if the machine is runing, False otherwise"""
        self.navigate_to(self, 'All', rhev_name=rhev_name)  # refresh
        vm = self.list_vms(rhev_name, vm_name)
        return vm['Power'].widget.read() == 'On'

    def vm_poweron(self, rhev_name, vm_name):
        """Starts the specified VM"""
        vm = self.list_vms(rhev_name, vm_name)
        if vm['Power'].widget.read() != 'On':
            vm['Actions'].widget.click(handle_alert=True)

    def vm_poweroff(self, rhev_name, vm_name):
        """Stops the specified VM"""
        vm = self.list_vms(rhev_name, vm_name)
        if vm['Power'].widget.read() == 'On':
            vm['Actions'].widget.click(handle_alert=True)


@navigator.register(ComputeResourceEntity, 'All')
class ShowAllComputeResources(NavigateStep):
    VIEW = ComputeResourcesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Compute Resources')


@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResource(NavigateStep):
    VIEW = ResourceProviderEditView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ComputeResourceEntity, 'Edit')
class EditExistingComputeResource(NavigateStep):
    VIEW = ResourceProviderEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(
            name=entity_name)['Actions'].widget.fill('Edit')


@navigator.register(ComputeResourceEntity, 'Detail')
class ComputeResourceDetail(NavigateStep):
    VIEW = ResourceProviderDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('rhev_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
