from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.architecture import (
    ArchitectureCreateView,
    ArchitectureDetailsView,
    ArchitecturesView,
)


class ArchitectureEntity(BaseEntity):
    endpoint_path = '/architectures'

    def create(self, values):
        """Create new architecture entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for architecture entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for created architecture entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update necessary values for architecture"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Remove existing architecture entity"""
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ArchitectureEntity, 'All')
class ShowAllArchitectures(NavigateStep):
    """Navigate to All Architectures page"""

    VIEW = ArchitecturesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Architectures')


@navigator.register(ArchitectureEntity, 'New')
class AddNewArchitecture(NavigateStep):
    """Navigate to Create Architecture page"""

    VIEW = ArchitectureCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ArchitectureEntity, 'Edit')
class EditArchitecture(NavigateStep):
    """Navigate to Edit Architecture page

    Args:
        entity_name: name of the architecture
    """

    VIEW = ArchitectureDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
