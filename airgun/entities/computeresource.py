from navmazing import NavigateToSibling

#constructor
from airgun.entities.base import BaseEntity
#navigator is for registering navigation steps, NavigateStep is from navmazing
from airgun.navigation import NavigateStep, navigator
from airgun.views.computeresource import (
    ComputeResourcesView,
    ResourceProviderDocker,
    ResourceProviderLibvirt,
    ResourceProviderOpenStack
    #ComputeResourcesEditView
)


class ComputeResourceEntity(BaseEntity):

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


@navigator.register(ComputeResourceEntity, 'All')
class ShowAllActivationComputeResources(NavigateStep):
    VIEW = ComputeResourcesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Compute Resources')


@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResourceDocker(NavigateStep):
    VIEW = ResourceProviderDocker

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)

@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResourceLibvirt(NavigateStep):
    VIEW = ResourceProviderLibvirt

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)

@navigator.register(ComputeResourceEntity, 'New')
class AddNewComputeResourceOpenStack(NavigateStep):
    VIEW = ResourceProviderOpenStack

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)

"""
@navigator.register(ComputeResourceEntity, 'Edit')
class EditExistingComputeResource(NavigateStep):
    VIEW = ComputeResourcesEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()
"""
