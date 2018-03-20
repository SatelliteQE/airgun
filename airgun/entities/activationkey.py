from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.activationkey import (
    ActivationKeyDetailsView,
    ActivationKeyEditView,
    ActivationKeyView,

)


class ActivationKeyEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.action_list.fill('Remove')
        view.dialog.confirm()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def associate_product(self, entity_name, product_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.subscriptions.add.fill(product_name)


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


@navigator.register(ActivationKeyEntity, 'Edit')
class EditExistingActivationKey(NavigateStep):
    VIEW = ActivationKeyEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        self.parent.search(kwargs.get('entity_name'))
        self.parent.edit.click()
