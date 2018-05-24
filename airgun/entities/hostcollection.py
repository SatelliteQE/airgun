from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.hostcollection import (
    HostCollectionCreateView,
    HostCollectionEditView,
    HostCollectionsView,
)


class HostCollectionEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        view.dialog.confirm()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def associate_host(self, entity_name, host_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.hosts.resources.add(host_name)


@navigator.register(HostCollectionEntity, 'All')
class ShowAllHostCollections(NavigateStep):
    VIEW = HostCollectionsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Host Collections')


@navigator.register(HostCollectionEntity, 'New')
class AddNewHostCollections(NavigateStep):
    VIEW = HostCollectionCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HostCollectionEntity, 'Edit')
class EditHostCollections(NavigateStep):
    VIEW = HostCollectionEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
