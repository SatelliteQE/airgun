from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import OverviewDetailsView


class OverviewEntity(BaseEntity):

    def read(self):
        view = self.navigate_to(self, "Details")
        return view.read()


@navigator.register(OverviewEntity, "Details")
class OverviewDetails(InsightsNavigateStep):
    VIEW = OverviewDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Overview")
