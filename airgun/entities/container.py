from navmazing import NavigateToSibling
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.container import (
    ContainerView,
    ContainerCreateView
)


class ContainerEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.ContainerEnvironmentCreateView.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)


@navigator.register(ContainerEntity, 'All')
class ShowAllContainers(NavigateStep):
    """Navigate to All Containers screen"""
    VIEW = ContainerView

    def step(self, *args, **kwargs):
        self.view.menu.select('Containers', 'All Containers')


@navigator.register(ContainerEntity, 'New')
class AddNewContainer(NavigateStep):
    """Navigate to Create container screen"""
    VIEW = ContainerCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)
