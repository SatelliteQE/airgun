from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.computeresource import (
    ComputeResourceLibvirtImageCreateView,
    ComputeResourceLibvirtImageEditView,
    ComputeResourcesView,
    ComputeResourceVMwareImageCreateView,
    ComputeResourceVMwareImageEditView,
    ResourceProviderCreateView,
    ResourceProviderDetailView,
    ResourceProviderEditView,
    ResourceProviderProfileView,
    ResourceProviderVMImport,
)


class ComputeResourceEntity(BaseEntity):
    endpoint_path = '/compute_resources'

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

    def read(self, entity_name, widget_names=None):
        """Read all values for existing compute resource entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

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
            view.virtual_machines.search.fill(expected_vm_name)
            return view.virtual_machines.table.row(name=expected_vm_name)
        return view.virtual_machines.table.rows()

    def search_virtual_machine(self, entity_name, value):
        """Search for compute resource virtual machine.

        :param str entity_name: The compute resource name.
        :param str value: The value to put in virtual machine tab search box.

        :return: The Compute resource virtual machines table rows values.
        """
        view = self.navigate_to(self, 'Detail', entity_name=entity_name)
        view.virtual_machines.search.fill(value)
        return view.virtual_machines.table.read()

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

    def vm_import(self, entity_name, vm_name, hostgroup, location, org=None, name=None):
        """Imports the specified VM"""
        view = self.navigate_to(self, 'VMImport', entity_name=entity_name, vm_name=vm_name)
        if name:
            view.fill({'host.name': name})
        if org:
            view.fill({'host.organization': org})
        view.fill({'host.hostgroup': hostgroup, 'host.location': location})
        view.submit.click()

    def update_computeprofile(self, entity_name, compute_profile, values):
        """Update specific compute profile attributes through CR detail view"""
        view = self.navigate_to(
            self, 'Profile', entity_name=entity_name, compute_profile=compute_profile
        )
        with self.browser.ignore_ensure_page_safe_timeout():
            view.fill(values)
            view.submit.click()

    def read_computeprofile(self, entity_name, compute_profile, widget_names=None):
        """Read specific compute profile attributes through CR detail view"""
        view = self.navigate_to(
            self, 'Profile', entity_name=entity_name, compute_profile=compute_profile
        )
        return view.read(widget_names=widget_names)

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
        view.images.filterbox.fill(value)
        return view.images.table.read()

    def read_image(self, entity_name, image_name, widget_names=None):
        """Read from compute resource image edit view.

        :param str entity_name: The compute resource name.
        :param str image_name: The existing compute resource image name to read.
        :returns: The edit view widgets values
        """
        view = self.navigate_to(self, 'Edit Image', entity_name=entity_name, image_name=image_name)
        return view.read(widget_names=widget_names)

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
        view.images.filterbox.fill(image_name)
        view.images.table.row(name=image_name)['Actions'].widget.fill('Destroy')
        self.browser.handle_alert()
        self.browser.plugin.ensure_page_safe()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ComputeResourceEntity, 'All')
class ShowAllComputeResources(NavigateStep):
    VIEW = ComputeResourcesView

    @retry_navigation
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
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Edit')

    def post_navigate(self, *args, **kwargs):
        """Select Compute resource tab for initialization"""
        self.view.compute_resource.click()

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return (
            self.view.is_displayed
            and self.view.breadcrumb.locations[0] == 'Compute Resources'
            and self.view.breadcrumb.read() == f'Edit {entity_name}'
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
            'Compute profile'
        ].widget.click()

    def am_i_here(self, *args, **kwargs):
        if not self.view.is_displayed:
            return False

        compute_profile = kwargs.get('compute_profile')
        entity_name = kwargs.get('entity_name')
        breadcrumbs = self.view.breadcrumb.locations

        return (
            breadcrumbs[1].startswith(entity_name)
            and breadcrumbs[3].endswith(compute_profile)
        )


@navigator.register(ComputeResourceEntity, 'VMImport')
class ComputeResourceVMImport(NavigateStep):
    VIEW = ResourceProviderVMImport

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.navigate_to(self.obj, 'Detail', entity_name=entity_name)

    def step(self, *args, **kwargs):
        vm_name = kwargs.get('vm_name')
        self.parent.virtual_machines.search.fill(vm_name)
        self.parent.virtual_machines.actions.fill('Import as managed Host')


class ComputeResourceImageProvider(NavigateStep):
    """Base class for image create and edit views, that need to dynamically define the view type
    (that depend from compute resource provider) before reaching navigation destination.
    """

    PROVIDER_VIEWS = {}

    def prerequisite(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        parent_view = self.navigate_to(self.obj, 'Detail', entity_name=entity_name)
        provider = parent_view.compute_resource.table.row(property='Provider')['Value'].read()
        view = self.PROVIDER_VIEWS.get(provider)
        if not view:
            raise ValueError(
                f'Provider type "{provider}" for class "{self.__class__.__name__}" not implemented'
            )
        self.VIEW = view
        return parent_view

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed


@navigator.register(ComputeResourceEntity, 'Create Image')
class ComputeResourceImageCreate(ComputeResourceImageProvider):
    PROVIDER_VIEWS = {
        'VMware': ComputeResourceVMwareImageCreateView,
        'Libvirt': ComputeResourceLibvirtImageCreateView,
    }

    def step(self, *args, **kwargs):
        self.parent.create_image.click()


@navigator.register(ComputeResourceEntity, 'Edit Image')
class ComputeResourceImageEdit(ComputeResourceImageProvider):
    PROVIDER_VIEWS = {
        'VMware': ComputeResourceVMwareImageEditView,
        'Libvirt': ComputeResourceLibvirtImageEditView,
    }

    def step(self, *args, **kwargs):
        image_name = kwargs.get('image_name')
        self.parent.images.filterbox.fill(image_name)
        self.parent.images.table.row(name=image_name)['Actions'].widget.fill('Edit')
