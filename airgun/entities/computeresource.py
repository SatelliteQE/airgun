from navmazing import NavigateToSibling
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeresource import (
    ComputeResourcesView,
    ResourceProviderDetailsView,
)


class ComputeResourceEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def edit(self, name, values):
        view = self.navigate_to(self, 'Edit', entity_name=name)
        view.fill(values)
        view.submit.click()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def delete(self, value):
        view = self.navigate_to(self, 'All')
        view.search(value)
        view.action_list.fill('Delete')
        self.browser.handle_alert()


@navigator.register(ComputeResourceEntity, 'All')
class ShowAllComputeResources(NavigateStep):
    VIEW = ComputeResourcesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Compute Resources')


@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResource(NavigateStep):
    VIEW = ResourceProviderDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ComputeResourceEntity, 'Edit')
class EditExistingComputeResource(NavigateStep):
    VIEW = ResourceProviderDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.browser.click(self.parent.edit)
