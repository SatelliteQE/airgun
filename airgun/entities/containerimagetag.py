from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.containerimagetag import (
    ContainerImageTagDetailsView,
    ContainerImageTagsView,
)


class ContainerImageTagEntity(BaseEntity):

    def search(self, value):
        """Search for specific Container Image Tag

        :param value: search query to type into search field
        :return: container image tag that match
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        """Reads details of specific Container Image Tag

        :param entity_name: name of Container Image Tag
        :return: dict with properties of Container Image Tag
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.read()


@navigator.register(ContainerImageTagEntity, 'All')
class ShowAllContainerImageTags(NavigateStep):
    """Navigate to All Container Image Tags screen."""
    VIEW = ContainerImageTagsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Container Image Tags')


@navigator.register(ContainerImageTagEntity, 'Details')
class ReadContainerImageTag(NavigateStep):
    """Navigate to Container Image Tag details page

        Args:
        entity_name: name of Container Image Tag
    """
    VIEW = ContainerImageTagDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
