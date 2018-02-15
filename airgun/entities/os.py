from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.os import OperatingSystemView, OperatingSystemDetailsView


class OperatingSystemEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.searchbox.search(value)


@navigator.register(OperatingSystemEntity, 'All')
class ShowAllOperatingSystems(NavigateStep):
    VIEW = OperatingSystemView

    def step(self, *args, **kwargs):
        # TODO: No prereq yet
        self.view.menu.select('Hosts', 'Operating systems')


@navigator.register(OperatingSystemEntity, 'New')
class AddNewOperatingSystem(NavigateStep):
    VIEW = OperatingSystemDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)
