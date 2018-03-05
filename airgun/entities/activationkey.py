from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.activationkey import (
    ActivationKeyView,
    ActivationKeyDetailsView,
)


class ActivationKeyEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)


@navigator.register(ActivationKeyEntity, 'All')
class ShowAllActivationKeys(NavigateStep):
    VIEW = ActivationKeyView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Activation Keys')


@navigator.register(ActivationKeyEntity, 'New')
class AddNewActivationKey(NavigateStep):
    VIEW = ActivationKeyDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)
