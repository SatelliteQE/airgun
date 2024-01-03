from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.virtwho_configure import (
    VirtwhoConfigureCreateView,
    VirtwhoConfigureDetailsView,
    VirtwhoConfigureEditView,
    VirtwhoConfiguresView,
)


class VirtwhoConfigureEntity(BaseEntity):
    endpoint_path = '/foreman_virt_who_configure/configs'

    def _reset_values(self, values):
        mapping = {
            'esx': 'VMware vSphere / vCenter (esx)',
            'xen': 'XenServer (xen)',
            'hyperv': 'Microsoft Hyper-V (hyperv)',
            'rhevm': 'Red Hat Virtualization Hypervisor (rhevm)',
            'libvirt': 'libvirt',
            'kubevirt': 'Container-native virtualization',
            'ahv': 'Nutanix AHV (ahv)',
        }
        vals = values.copy()
        if 'hypervisor_type' in vals:
            hypervisor_value = vals['hypervisor_type']
            vals.update({'hypervisor_type': mapping[hypervisor_value]})
        return vals

    def check_create_permission(self):
        """Check if the config can be viewed/created"""
        try:
            view = self.navigate_to(self, 'All')
        except Exception:  # noqa: BLE001 - TODO: determine proper exception
            return {"can_view": False, "can_create": False}
        return {"can_view": True, "can_create": view.new.is_displayed}

    def check_update_permission(self, entity_name=None):
        """Check if the config can be deleted/edited"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return {"can_delete": view.delete.is_displayed, "can_edit": view.edit.is_displayed}

    def create(self, values):
        """Create new virtwho configure entity"""
        view = self.navigate_to(self, 'New')
        values = self._reset_values(values)
        view.fill(values)
        view.submit.click()
        view.flash.assert_message(f"Success alert: Successfully created {values['name']}.")
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for virtwho configure"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def edit(self, name, values):
        """Edit specific virtwho configure values"""
        view = self.navigate_to(self, 'Edit', entity_name=name)
        values = self._reset_values(values)
        view.fill(values)
        view.submit.click()
        if 'name' in values:
            view.flash.assert_message(f"Success alert: Successfully updated {values['name']}.")
        else:
            view.flash.assert_message(f"Success alert: Successfully updated {name}.")
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Read all values for existing virtwho configure entity"""
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def delete(self, value):
        """Delete specific virtwho configure"""
        view = self.navigate_to(self, 'All')
        view.search(value)
        view.table.row(name=value)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_message(f"Success alert: Successfully deleted {value}.")
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(VirtwhoConfigureEntity, 'All')
class ShowAllVirtwhoConfigures(NavigateStep):
    """Navigate to All Activation Keys page"""

    VIEW = VirtwhoConfiguresView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Virt-who configurations')


@navigator.register(VirtwhoConfigureEntity, 'New')
class AddNewVirtwhoConfigure(NavigateStep):
    """Navigate to New Virtwho Configure page"""

    VIEW = VirtwhoConfigureCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(VirtwhoConfigureEntity, 'Edit')
class EditExistingVirtwhoConfigure(NavigateStep):
    """Navigate to Edit Virtwho Configure page

    Args:
        entity_name: name of the virtwho configure
    """

    VIEW = VirtwhoConfigureEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Edit')


@navigator.register(VirtwhoConfigureEntity, 'Details')
class DetailsVirtwhoConfigure(NavigateStep):
    """Navigate to Details page by clicking on necessary name in the table

    Args:
        entity_name: name of the configure
    """

    VIEW = VirtwhoConfigureDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
