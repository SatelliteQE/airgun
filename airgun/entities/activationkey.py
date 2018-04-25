from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.activationkey import (
    ActivationKeyCreateView,
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
        view.actions.fill('Remove')
        view.dialog.confirm()

    def search(self, value, expected_result=None):
        view = self.navigate_to(self, 'All')
        return view.search(value, expected_result)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def add_subscription(self, entity_name, subscription_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.subscriptions.resources.add(subscription_name)

    def add_host_collection(self, entity_name, hc_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.host_collections.resources.add(hc_name)
        assert view.flash.is_displayed
        view.flash.assert_no_error()

    def remove_host_collection(self, entity_name, hc_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.host_collections.resources.remove(hc_name)
        assert view.flash.is_displayed
        view.flash.assert_no_error()


@navigator.register(ActivationKeyEntity, 'All')
class ShowAllActivationKeys(NavigateStep):
    VIEW = ActivationKeyView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Activation Keys')


@navigator.register(ActivationKeyEntity, 'New')
class AddNewActivationKey(NavigateStep):
    VIEW = ActivationKeyCreateView

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
