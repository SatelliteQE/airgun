from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.activationkey import ActivationKeyCreateView
from airgun.views.activationkey import ActivationKeyEditView
from airgun.views.activationkey import ActivationKeysView


class ActivationKeyEntity(BaseEntity):
    endpoint_path = '/activation_keys'

    def create(self, values):
        """Create new activation key entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Remove existing activation key entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for activation key"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Read all values for created activation key entity"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update necessary values for activation key"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def add_subscription(self, entity_name, subscription_name):
        """Add subscription to activation key

        :param entity_name: Activation key name
        :param subscription_name: Name of subscription to be added to activation key
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.subscriptions.resources.add(subscription_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_host_collection(self, entity_name, hc_name):
        """Add host collection to activation key

        :param entity_name: Activation key name
        :param hc_name: Name of host collection to be added to activation key
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.host_collections.resources.add(hc_name)
        assert view.flash.is_displayed
        view.flash.assert_no_error()
        view.flash.dismiss()

    def remove_host_collection(self, entity_name, hc_name):
        """Remove host collection from activation key

        :param entity_name: Activation key name
        :param hc_name: Name of host collection to be removed from activation key
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.host_collections.resources.remove(hc_name)
        assert view.flash.is_displayed
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ActivationKeyEntity, 'All')
class ShowAllActivationKeys(NavigateStep):
    """Navigate to All Activation Keys page"""
    VIEW = ActivationKeysView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Activation Keys')


@navigator.register(ActivationKeyEntity, 'New')
class AddNewActivationKey(NavigateStep):
    """Navigate to New Activation Key page"""
    VIEW = ActivationKeyCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.browser.click(self.parent.new)


@navigator.register(ActivationKeyEntity, 'Edit')
class EditExistingActivationKey(NavigateStep):
    """Navigate to Edit Activation Key page

    Args:
        entity_name: name of the activation key
    """
    VIEW = ActivationKeyEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
