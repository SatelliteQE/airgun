from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.entities.computeresource import ComputeResourceEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeprofile import (
    ComputeProfileCreateView,
    ComputeProfileRenameView,
    ComputeProfilesView,
    ComputeProfileDetailView,
)
from airgun.views.computeresource import (
    ResourceProviderDetailView,
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

    def update(self, entity_name, compute_resource, values):
        """Update specific compute profile values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.table.row(compute_resource=compute_resource)[
            'Compute Resource'].widget.click()
        view.fill(values)
        view.submit.click()

    def update_through_CR(self, entity_name, compute_profile, values):
        """Update specific compute profile values through CR detail view"""
        view = self.navigate_to(self, 'Edit2', entity_name=entity_name)
        view.compute_profiles.table.row(compute_profile=compute_profile)[
            'Compute profile'].widget.click()
        view.fill(values)
        view.submit.click()

    def read(self, entity_name, compute_resource):
        """Read all values for existing compute profile entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.table.row(compute_resource=compute_resource)[
            'Compute Resource'].widget.click()
        return view.read()

    def delete(self, entity_name):
        """Delete specific compute profile"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()

    def select_profile(self, entity_name, compute_profile):
        """Select specific compute profile on Compute profiles tab
        in CR detail view"""
        view = self.navigate_to(self, 'Edit2', entity_name=entity_name)
        view.compute_profiles.table.row(compute_profile=compute_profile)[
            'Compute profile'].widget.click()
        view.submit.click()


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
        self.parent.actions.fill('Rename')


@navigator.register(ComputeProfileEntity, 'Edit')
class EditComputeProfile(NavigateStep):
    VIEW = ComputeProfileDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ComputeProfileEntity, 'Edit2')
class EditComputeProfile2(NavigateStep):
    VIEW = ResourceProviderDetailView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(ComputeResourceEntity, 'All', **kwargs)

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
