from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import ActionsDetailsView


class ActionEntity(BaseEntity):

    def read(self):
        """Read the content of the view."""
        view = self.navigate_to(self, "Details")
        return view.read()


@navigator.register(ActionEntity, "Details")
class ActionDetails(InsightsNavigateStep):
    """Navigate to Red Hat Access Insights Actions screen."""
    VIEW = ActionsDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Actions")
