from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.puppet_class import PuppetClassDetailsView, PuppetClassesView


class PuppetClassEntity(BaseEntity):

    def search(self, value):
        """Search for puppet class entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Read puppet class entity values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        """Update puppet class values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete puppet class entity"""
        view = self.navigate_to(self, 'All')
        view.table.row(class_name=entity_name)['Actions'].widget.click(
            handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(PuppetClassEntity, 'All')
class ShowAllPuppetClasses(NavigateStep):
    """Navigate to All Puppet Classes screen."""
    VIEW = PuppetClassesView

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
        self.parent.table.row(
            class_name=entity_name)['Class name'].widget.click()
