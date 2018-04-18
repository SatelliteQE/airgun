import attr

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView


@attr.s
class LocationEntity(BaseEntity):
    name = attr.ib()

    def select(self):
        self.navigate_to(self, 'Context')


class LocationView(BaseLoggedInView):
    @property
    def is_displayed(self):
        current_loc = self.taxonomies.current_loc()
        return (current_loc == self.context['object'].name
                if len(self.context['object'].name) <= 30
                else self.context['object'].name[:27] + '...')


@navigator.register(LocationEntity, 'Context')
class SelectLocationContext(NavigateStep):
    VIEW = BaseLoggedInView

    def step(self, *args, **kwargs):
        self.view.taxonomies.select_loc(self.obj.name)
