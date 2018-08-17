from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.rhai import ManageDetailsView


class ManageEntity(BaseEntity):

    def _toggle_service(self, state):
        view = self.navigate_to(self, "Details")
        if view.enable_service.fill(state):
            view.save.click()

    def enable_service(self):
        self._toggle_service(True)

    def disable_service(self):
        self._toggle_service(False)

    def read(self):
        view = self.navigate_to(self, "Details")
        view.check_connection.click()
        return view.read()


@navigator.register(ManageEntity, "Details")
class ManageDetails(NavigateStep):
    VIEW = ManageDetailsView

    def step(self, *args, **kwargs):
        self.view.menu.select("Insights", "Manage")
