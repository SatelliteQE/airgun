from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeprofile import (
    ComputeProfileCreateView,
    ComputeProfileView,
)


class ComputeProfileEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def rename(self, old_name, new_name):
        view = self.navigate_to(self, 'Rename', entity_name=old_name)
        view.actions.fill('Rename')
        view.fill(new_name)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.actions.fill('Delete')
        self.browser.handle_alert()


@navigator.register(ComputeProfileEntity, 'All')
class ShowAllComputeProfile(NavigateStep):
    VIEW = ComputeProfileView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Infrastructure', 'Compute Profiles')


@navigator.register(ComputeProfileEntity, 'New')
class AddNewComputeProfile(NavigateStep):
    VIEW = ComputeProfileCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)


@navigator.register(ComputeProfileEntity, 'Rename')
class RenameComputeProfile(NavigateStep):
    VIEW = ComputeProfileCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
