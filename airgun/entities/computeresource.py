from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeresource import (
    ComputeResourcesView,
    ResourceProviderCreateView,
    ResourceProviderEditView,
    ResourceProviderDetailView,
    ComputeResourceRHVImageCreateView,
    ComputeResourceRHVImageEditView,
    ComputeResourceVMwareImageCreateView,
    ComputeResourceVMwareImageEditView,
    ResourceProviderProfileView,
    ResourceProviderVMImport,
)


class ComputeResourceEntity(BaseEntity):

    def create(self, values):
        """Create new compute resource entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for compute resource entity and return table row
        that contains that entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def edit(self, name, values):
        """Edit specific compute resource values"""
        view = self.navigate_to(self, 'Edit', entity_name=name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name):
        """Read all values for existing compute resource entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def delete(self, value):
        """Delete specific compute profile"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        view.table.row(name=value)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def list_vms(self, entity_name, expected_vm_name=None):
        """Returns all the VMs on the CR or VM with specified name"""
        view = self.navigate_to(self, 'Detail', entity_name=entity_name)
        if expected_vm_name:
            view.virtual_machines.search(expected_vm_name)
            return view.virtual_machines.table.row(name=expected_vm_name)
        return view.virtual_machines.table.rows()

    def search_virtual_machine(self, entity_name, value):
        """Search for compute resource virtual machine.

        :param str entity_name: The compute resource name.
        :param str value: The value to put in virtual machine tab search box.

        :return: The Compute resource virtual machines table rows values.
        """
        view = self.navigate_to(self, 'Detail', entity_name=entity_name)
        return view.virtual_machines.search(value)

    def vm_status(self, entity_name, vm_name):
        """Returns True if the machine is running, False otherwise"""
        vm = self.list_vms(entity_name, vm_name)
        return vm['Power'].widget.read() == 'On'

    def vm_poweron(self, entity_name, vm_name):
        """Starts the specified VM"""
        vm = self.list_vms(entity_name, vm_name)
        if vm['Power'].widget.read() != 'On':
            vm['Actions'].widget.click(handle_alert=True)

    def vm_poweroff(self, entity_name, vm_name):
        """Stops the specified VM"""
        vm = self.list_vms(entity_name, vm_name)
        if vm['Power'].widget.read() == 'On':
            vm['Actions'].widget.click(handle_alert=True)

    def vm_import(self, entity_name, vm_name, hostgroup, location):
        """Imports the specified VM"""
        view = self.navigate_to(self, 'VMImport',
                                entity_name=entity_name, vm_name=vm_name)
        view.fill({'host.hostgroup': hostgroup, 'host.location': location})
        view.submit.click()

    def update_computeprofile(self, entity_name, compute_profile, values):
        """Update specific compute profile attributes through CR detail view"""
        view = self.navigate_to(
            self,
            'Profile',
            entity_name=entity_name,
            compute_profile=compute_profile
        )
        view.fill(values)
        view.submit.click()

    def read_computeprofile(self, entity_name, compute_profile):
        """Read specific compute profile attributes through CR detail view"""
        view = self.navigate_to(
            self,
            'Profile',
            entity_name=entity_name,
            compute_profile=compute_profile
        )
        return view.read()

    def create_image(self, entity_name, values):
        """Create a compute resource image.

        :param str entity_name: The compute resource name
        :param dict values: The image properties
        """
        view = self.navigate_to(self, 'Create Image', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search_images(self, entity_name, value):
        """Search for compute resource images.

        :param str entity_name: The compute resource name.
        :param str value: The value to put in images tab search box.

        :return: The Compute resource images table rows values.
        """
        view = self.navigate_to(self, 'Detail', entity_name=entity_name)
        return view.images.search(value)

    def read_image(self, entity_name, image_name):
        """Read from compute resource image edit view.

        :param str entity_name: The compute resource name.
        :param str image_name: The existing compute resource image name to read.
        :returns: The edit view widgets values
        """
        view = self.navigate_to(self, 'Edit Image', entity_name=entity_name, image_name=image_name)
        return view.read()

    def update_image(self, entity_name, image_name, values):
        """Update compute resource image properties.

        :param str entity_name: The compute resource name.
        :param str image_name: The existing compute resource image name to update
        :param dict values: The image new properties.
        """
        view = self.navigate_to(self, 'Edit Image', entity_name=entity_name, image_name=image_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete_image(self, entity_name, image_name):
        """Delete compute resource image.

        :param str entity_name: The compute resource name.
        :param str image_name: The existing compute resource image name to delete.
        """
        view = self.navigate_to(self, 'Detail', entity_name=entity_name)
        view.images.search(image_name)
        view.images.table.row(name=image_name)['Actions'].widget.fill('Destroy')
        self.browser.handle_alert()
        self.browser.plugin.ensure_page_safe()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ComputeResourceEntity, 'All')
class ShowAllComputeResources(NavigateStep):
    VIEW = ComputeResourcesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Compute Resources')


@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResource(NavigateStep):
    VIEW = ResourceProviderCreateView

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

    def post_navigate(self, _tries, *args, **kwargs):
        """Select Compute resource tab for initialization"""
        self.view.compute_resource.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[0] == 'Compute Resources'
                and self.view.breadcrumb.read() == 'Edit {}'.format(entity_name)
        )


@navigator.register(ComputeResourceEntity, 'Detail')
class ComputeResourceDetail(NavigateStep):
    VIEW = ResourceProviderDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return (
                self.view.is_displayed
                and self.view.breadcrumb.locations[0] == 'Compute Resources'
                and self.view.breadcrumb.read() == entity_name
        )


@navigator.register(ComputeResourceEntity, 'Profile')
class ComputeResourceProfileDetail(NavigateStep):
    VIEW = ResourceProviderProfileView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Detail', **kwargs)

    def step(self, *args, **kwargs):
        compute_profile = kwargs.get('compute_profile')
        self.parent.compute_profiles.table.row(compute_profile=compute_profile)[
            'Compute profile'].widget.click()


@navigator.register(ComputeResourceEntity, 'VMImport')
class ComputeResourceVMImport(NavigateStep):
    VIEW = ResourceProviderVMImport

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.navigate_to(self.obj, 'Detail', entity_name=entity_name)

    def step(self, *args, **kwargs):
        vm_name = kwargs.get('vm_name')
        self.parent.virtual_machines.search(vm_name)
        self.parent.virtual_machines.actions.fill("Import")


class ComputeResourceImageProvider(NavigateStep):
    """Base class for image create and edit views, that need to dynamically define the view type
    (that depend from compute resource provider) before reaching navigation destination.
    """
    PROVIDER_VIEWS = dict()

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        parent_view = self.navigate_to(self.obj, 'Detail', entity_name=entity_name)
        provider = parent_view.compute_resource.table.row(property='Provider')['Value'].read()
        view = self.PROVIDER_VIEWS.get(provider)
        if not view:
            raise ValueError('Provider type "{0}" for class "{1}" not implemented'.format(
                provider, self.__class__.__name__))
        self.VIEW = view
        return parent_view

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed


@navigator.register(ComputeResourceEntity, 'Create Image')
class ComputeResourceImageCreate(ComputeResourceImageProvider):

    PROVIDER_VIEWS = dict(
        RHV=ComputeResourceRHVImageCreateView,
        VMware=ComputeResourceVMwareImageCreateView,
    )

    def step(self, *args, **kwargs):
        self.parent.create_image.click()


@navigator.register(ComputeResourceEntity, 'Edit Image')
class ComputeResourceImageEdit(ComputeResourceImageProvider):

    PROVIDER_VIEWS = dict(
        RHV=ComputeResourceRHVImageEditView,
        VMware=ComputeResourceVMwareImageEditView,
    )

    def step(self, *args, **kwargs):
        image_name = kwargs.get('image_name')
        self.parent.images.search(image_name)
        self.parent.images.table.row(name=image_name)['Actions'].widget.fill('Edit')
