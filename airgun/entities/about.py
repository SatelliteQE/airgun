from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.about import AboutView


class AboutEntity(BaseEntity):
    endpoint_path = '/about'


@navigator.register(AboutEntity, 'All')
class ShowAboutPage(NavigateStep):
    """Navigate to About page."""

    VIEW = AboutView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'About')
