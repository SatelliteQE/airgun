from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.rhai import OverviewDetailsView


class OverviewEntity(BaseEntity):

    def read(self, widget_names=None):
        view = self.navigate_to(self, "Details")
        return view.read(widget_names=widget_names)


@navigator.register(OverviewEntity, "Details")
class OverviewDetails(NavigateStep):
    VIEW = OverviewDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Overview")
