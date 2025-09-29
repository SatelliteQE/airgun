from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.fact import HostFactView


class FactValueEntity(BaseEntity):
    endpoint_path = "/fact_values"


@navigator.register(FactValueEntity, "All")
class ShowFactValuePage(NavigateStep):
    """Navigate to Fact Values page."""

    VIEW = HostFactView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select("Monitor", "Facts")
