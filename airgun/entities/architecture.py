from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import BaseNavigator, menu_click, navigator
from airgun.views.architecture import ArchitectureView, ArchitectureDetailsView


class ArchitectureEntity(BaseEntity):

    def create_architecture(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit_data()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search_element.search(value)

    def view_architecture(self, name):
        view = self.navigate_to(self, 'All')
        view.search_element.search(name)
        view = self.navigate_to(self, 'Edit')
        return view.read()


@navigator.register(ArchitectureEntity, 'All')
class ShowAllArchitectures(BaseNavigator):
    VIEW = ArchitectureView

    def step(self, *args, **kwargs):
        menu_click(
            ["//a[@id='hosts_menu']", self.view.page_navigate_locator],
            self.view.browser
        )


@navigator.register(ArchitectureEntity, 'New')
class AddNewArchitecture(BaseNavigator):
    VIEW = ArchitectureDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)


@navigator.register(ArchitectureEntity, 'Edit')
class EditExistingArchitecture(BaseNavigator):
    VIEW = ArchitectureDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.entity_navigate_locator, ensure_page_safe=True)
        self.parent.browser.click(self.parent.entity_navigate_locator)
