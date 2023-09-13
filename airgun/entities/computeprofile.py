from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.computeprofile import (
    ComputeProfileCreateView,
    ComputeProfileDetailView,
    ComputeProfileRenameView,
    ComputeProfilesView,
)


class ComputeProfileEntity(BaseEntity):
    endpoint_path = '/compute_profiles'

    def create(self, values):
        """Create new compute profile entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

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
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete specific compute profile"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def list_resources(self, entity_name):
        """List of compute resources that applied to specific
        compute profile"""
        view = self.navigate_to(self, 'List', entity_name=entity_name)
        return view.table.read()


@navigator.register(ComputeProfileEntity, 'All')
class ShowAllComputeProfiles(NavigateStep):
    """Navigate to All Compute Profiles page"""

    VIEW = ComputeProfilesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Compute Profiles')


@navigator.register(ComputeProfileEntity, 'New')
class AddNewComputeProfile(NavigateStep):
    """Navigate to Create Compute Profile page"""

    VIEW = ComputeProfileCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ComputeProfileEntity, 'Rename')
class RenameComputeProfile(NavigateStep):
    """Navigate to Edit Compute Profile page that basically does rename only

    Args:
        entity_name: name of the compute profile to be renamed
    """

    VIEW = ComputeProfileRenameView

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Rename')


@navigator.register(ComputeProfileEntity, 'List')
class ListComputeResources(NavigateStep):
    """Navigate to list of Compute Resources for particular Compute Profile

    Args:
        entity_name: name of the compute profile to be listed
    """

    VIEW = ComputeProfileDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
