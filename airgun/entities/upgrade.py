from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.upgrade import UpgradeView


class UpgradeEntity(BaseEntity):
    endpoint_path = '/upgrade'

    def documentation_links(self):
        view = self.navigate_to(self, 'Home')
        return view.documentation_links()


@navigator.register(UpgradeEntity, 'Home')
class Upgrade(NavigateStep):
    """Navigate to Satellite Upgrade screen."""

    VIEW = UpgradeView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Satellite Upgrade')
