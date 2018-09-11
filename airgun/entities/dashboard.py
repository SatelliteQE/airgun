from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.dashboard import DashboardView


class DashboardEntity(BaseEntity):

    def search(self, value):
        """Initiate search procedure that applied on all dashboard widgets.
        Return widgets values as a result
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self):
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
        if self.view.browser.element(self.view.AUTO_REFRESH).get_attribute(
                'data-original-title') == 'Auto refresh on':
            self.view.browser.element(self.view.AUTO_REFRESH).click()
