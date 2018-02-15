from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView


class LocationEntity(BaseEntity):
    def select(self, loc_name):
        self.navigate_to(self, 'Context', loc_name=loc_name)


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
