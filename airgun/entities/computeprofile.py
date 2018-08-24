from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeprofile import (
    ComputeProfileCreateView,
    ComputeProfileRenameView,
    ComputeProfilesView,
    ComputeProfileDetailView,
)


class ComputeProfileEntity(BaseEntity):

    def create(self, values):
        """Create new compute profile entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for compute profile entity and return table row
        that contains that entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def rename(self, old_name, new_name):
        """Rename specific compute profile"""
        view = self.navigate_to(self, 'Rename', entity_name=old_name)
        view.fill(new_name)
        view.submit.click()

    def delete(self, entity_name):
        """Delete specific compute profile"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def list_resources(self, entity_name):
        """List of compute resources that applied to specific
        compute profile"""
        view = self.navigate_to(self, 'List', entity_name=entity_name)
        return view.table.read()


@navigator.register(ComputeProfileEntity, 'All')
class ShowAllComputeProfiles(NavigateStep):
    VIEW = ComputeProfilesView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Infrastructure', 'Compute Profiles')


@navigator.register(ComputeProfileEntity, 'New')
class AddNewComputeProfile(NavigateStep):
    VIEW = ComputeProfileCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ComputeProfileEntity, 'Rename')
class RenameComputeProfile(NavigateStep):
    VIEW = ComputeProfileRenameView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(
            name=entity_name)['Actions'].widget.fill('Rename')


@navigator.register(ComputeProfileEntity, 'List')
class ListComputeResources(NavigateStep):
    VIEW = ComputeProfileDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
