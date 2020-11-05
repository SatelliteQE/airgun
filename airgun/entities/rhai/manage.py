from airgun.entities.base import BaseEntity
from airgun.entities.rhai.base import InsightsNavigateStep
from airgun.navigation import navigator
from airgun.views.rhai import ManageDetailsView


class ManageEntity(BaseEntity):
    endpoint_path = '/redhat_access/insights/manage'

    def _toggle_service(self, state):
        view = self.navigate_to(self, "Details")
        if view.enable_service.fill(state):
            view.save.click()

    def enable_service(self):
        """Enable the service."""
        self._toggle_service(True)

    def disable_service(self):
        """Disable the service."""
        self._toggle_service(False)

    def read(self, widget_names=None):
        """Read the content of the view."""
        view = self.navigate_to(self, "Details")
        view.check_connection.click()
        return view.read(widget_names=widget_names)


@navigator.register(ManageEntity, "Details")
class ManageDetails(InsightsNavigateStep):
    """Navigate to Red Hat Access Insights Manage screen."""

    VIEW = ManageDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Manage")
