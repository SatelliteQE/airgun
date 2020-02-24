from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.dashboard import DashboardView


class DashboardEntity(BaseEntity):

    def search(self, value):
        """Initiate search procedure that applied on all dashboard widgets.
        Return widgets values as a result
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, widget_name):
        """Read specific widget value"""
        view = self.navigate_to(self, 'All')
        if widget_name not in view.widget_names:
            raise ValueError('Provide correct widget name to be read')
        return getattr(view, widget_name).read()

    def read_all(self):
        """Read all dashboard widgets values"""
        view = self.navigate_to(self, 'All')
        return view.read()

    def action(self, values):
        """Perform action against specific widget. In most cases, re-direction
        to another entity is happened
        """
        view = self.navigate_to(self, 'All')
        view.fill(values)


@navigator.register(DashboardEntity, 'All')
class OpenDashboard(NavigateStep):
    """Navigate to Dashboard page"""
    VIEW = DashboardView

    def step(self, *args, **kwargs):
        self.view.menu.select('Monitor', 'Dashboard')

    def post_navigate(self, _tries=0, *args, **kwargs):
        """Disable auto-refresh feature for dashboard entity each time
        navigation to the page is finished
        """
        self.view.refresh.fill(False)
