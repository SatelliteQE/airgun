from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.puppet_class import PuppetClassDetailsView
from airgun.views.puppet_class import PuppetClassesView


class PuppetClassEntity(BaseEntity):
    endpoint_path = '/foreman_puppet/puppetclasses'

    def search(self, value):
        """Search for puppet class entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read puppet class entity values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_smart_class_parameter(self, entity_name, parameter_name):
        """Read smart class parameter values for specific puppet class"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.smart_class_parameter.filter.fill(parameter_name)
        view.smart_class_parameter.parameter_list.fill(parameter_name.replace('_', ' '))
        return view.smart_class_parameter.parameter.read()

    def update(self, entity_name, values):
        """Update puppet class values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete puppet class entity"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(class_name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(PuppetClassEntity, 'All')
class ShowAllPuppetClasses(NavigateStep):
    """Navigate to All Puppet Classes screen."""

    VIEW = PuppetClassesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Classes')


@navigator.register(PuppetClassEntity, 'Edit')
class EditPuppetClass(NavigateStep):
    """Navigate to Edit Puppet Class screen.

    Args:
        entity_name: name of puppet class
    """

    VIEW = PuppetClassDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(class_name=entity_name)['Class name'].widget.click()
