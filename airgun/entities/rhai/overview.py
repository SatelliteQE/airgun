from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import OverviewDetailsView


class OverviewEntity(BaseEntity):
    endpoint_path = "/redhat_access/insights"

    def read(self, widget_names=None):
        view = self.navigate_to(self, "Details")
        return view.read(widget_names=widget_names)


@navigator.register(OverviewEntity, "Details")
class OverviewDetails(InsightsNavigateStep):
    VIEW = OverviewDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Overview")
