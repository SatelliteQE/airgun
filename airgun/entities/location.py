

from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView

from airgun.views.location import (
    LocationCreateView,
    LocationsView,
)


class LocationEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

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
