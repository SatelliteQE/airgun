from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.architecture import ArchitectureView, ArchitectureDetailsView


class ArchitectureEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()


@navigator.register(ArchitectureEntity, 'All')
class ShowAllArchitectures(NavigateStep):
    VIEW = ArchitectureView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Hosts', 'Architectures')


@navigator.register(ArchitectureEntity, 'New')
class AddNewArchitecture(NavigateStep):
    VIEW = ArchitectureDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)


@navigator.register(ArchitectureEntity, 'Edit')
class EditArchitecture(NavigateStep):
    VIEW = ArchitectureDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.browser.wait_for_element(
            self.parent.edit, ensure_page_safe=True)
        self.parent.edit.click()
