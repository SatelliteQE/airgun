from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.subnet import SubnetView, SubnetDetailsView


class SubnetEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)


@navigator.register(SubnetEntity, 'All')
class ShowAllSubnets(NavigateStep):
    VIEW = SubnetView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Infrastructure', 'Subnets')


@navigator.register(SubnetEntity, 'New')
class AddNewSubnet(NavigateStep):
    VIEW = SubnetDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)
