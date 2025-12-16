from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.subnet import SubnetCreateView, SubnetEditView, SubnetsView


class SubnetEntity(BaseEntity):
    endpoint_path = '/subnets'

    def create(self, values):
        """Create new subnet"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific subnet"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read values for existing subnet"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update subnet values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete subnet"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)


@navigator.register(SubnetEntity, 'All')
class ShowAllSubnets(NavigateStep):
    """Navigate to All Subnets screen."""

    VIEW = SubnetsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Subnets')


@navigator.register(SubnetEntity, 'New')
class AddNewSubnet(NavigateStep):
    """Navigate to Create new Subnet screen."""

    VIEW = SubnetCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(SubnetEntity, 'Edit')
class EditSubnet(NavigateStep):
    """Navigate to Edit Subnet screen.

    Args:
       entity_name: name of subnet
    """

    VIEW = SubnetEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
