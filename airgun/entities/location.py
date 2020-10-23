from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.common import BaseLoggedInView
from airgun.views.location import LocationCreateView
from airgun.views.location import LocationsEditView
from airgun.views.location import LocationsView


class LocationEntity(BaseEntity):
    endpoint_path = '/locations'

    def create(self, values):
        """Create new location entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing location"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def read(self, entity_name, widget_names=None):
        """Read specific location details"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def search(self, value):
        """Search for location entity"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def update(self, entity_name, values):
        """Update necessary values for location"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def select(self, loc_name):
        """Select necessary location from context menu on the top of the page"""
        self.navigate_to(self, 'Context', loc_name=loc_name)


@navigator.register(LocationEntity, 'All')
class ShowAllLocations(NavigateStep):
    """Navigate to All Locations page"""

    VIEW = LocationsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Locations')


@navigator.register(LocationEntity, 'New')
class AddNewLocation(NavigateStep):
    """Navigate to Create Location page"""

    VIEW = LocationCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(LocationEntity, 'Edit')
class EditLocation(NavigateStep):
    """Navigate to Edit Location page

    Args:
        entity_name: name of the location
    """

    VIEW = LocationsEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(LocationEntity, 'Context')
class SelectLocationContext(NavigateStep):
    """Select Location from menu

    Args:
        loc_name: name of the location
    """

    VIEW = BaseLoggedInView

    def am_i_here(self, *args, **kwargs):
        loc_name = kwargs.get('loc_name')
        if len(loc_name) > 30:
            loc_name = loc_name[:27] + '...'
        return loc_name == self.view.taxonomies.current_loc

    def step(self, *args, **kwargs):
        loc_name = kwargs.get('loc_name')
        if not loc_name:
            raise ValueError('Specify proper value for loc_name parameter')
        self.view.taxonomies.select_loc(loc_name)
