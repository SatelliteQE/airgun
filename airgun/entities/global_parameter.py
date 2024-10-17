from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.global_parameter import GlobalParameterView


class GlobalParameterEntity(BaseEntity):
    endpoint_path = '/common_parameters'


@navigator.register(GlobalParameterEntity, 'All')
class ShowGlobalParameters(NavigateStep):
    """Navigate to Global Parameters page."""

    VIEW = GlobalParameterView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Global Parameters')
