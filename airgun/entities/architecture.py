from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.architecture import (
    ArchitectureCreateView,
    ArchitectureDetailsView,
    ArchitecturesView,
)


class ArchitectureEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.searchbox.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.click(
            handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ArchitectureEntity, 'All')
class ShowAllArchitectures(NavigateStep):
    VIEW = ArchitecturesView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Hosts', 'Architectures')


@navigator.register(ArchitectureEntity, 'New')
class AddNewArchitecture(NavigateStep):
    VIEW = ArchitectureCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(ArchitectureEntity, 'Edit')
class EditArchitecture(NavigateStep):
    VIEW = ArchitectureDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
