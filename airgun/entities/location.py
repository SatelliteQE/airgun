from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView

from airgun.views.location import (
    LocationCreateView,
    LocationsEditView,
    LocationsView,
)


class LocationEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def select(self, loc_name):
        self.navigate_to(self, 'Context', loc_name=loc_name)


@navigator.register(LocationEntity, 'All')
class ShowAllLocations(NavigateStep):
    VIEW = LocationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Locations')


@navigator.register(LocationEntity, 'New')
class AddNewLocation(NavigateStep):
    VIEW = LocationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(LocationEntity, 'Edit')
class EditLocation(NavigateStep):
    VIEW = LocationsEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(LocationEntity, 'Context')
class SelectLocationContext(NavigateStep):
    VIEW = BaseLoggedInView

    def am_i_here(self, *args, **kwargs):
        loc_name = kwargs.get('loc_name')
        current_loc = self.view.taxonomies.current_loc()
        if len(loc_name) > 30:
            loc_name = loc_name[:27] + '...'
        return current_loc == loc_name

    def step(self, *args, **kwargs):
        loc_name = kwargs.get('loc_name')
        if not loc_name:
            raise ValueError('Specify proper value for loc_name parameter')
        self.view.taxonomies.select_loc(loc_name)
