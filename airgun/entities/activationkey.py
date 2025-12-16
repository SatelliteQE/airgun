from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.activationkey import (
    ActivationKeyCreateView,
    ActivationKeyEditView,
    ActivationKeysView,
)


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
        self.browser.handle_alert()
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

    def get_repos(self, entity_name, repo_type='All'):
        """Read all values for repository sets on activation keys"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.repository_sets.repo_type.select_by_visible_text(repo_type)
        return view.repository_sets.table.read()

    def update(self, entity_name, values):
        """Update necessary values for activation key"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        filled_values = view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()
        return filled_values

    def update_ak_host_limit(self, entity_name, host_limit):
        """
        Update activation key host limit

        args:
            entity_name: Activation key name
            host_limit: Host limit for activation key. Can be either string 'unlimited' or an integer
        raises:
            ValueError: If host limit is not string 'unlimited' or an integer
        """

        if isinstance(host_limit, (str)):
            host_limit = host_limit.lower()
        # Check that host limit is string 'unlimited' or integer
        if (host_limit != 'unlimited') and (not isinstance(host_limit, (int))):
            raise ValueError("Host limit must be either string 'unlimited' or an integer")

        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.host_limit_edit_btn.click()
        view.details.unlimited_content_host_checkbox.fill(host_limit == 'unlimited')
        if host_limit != 'unlimited':
            view.details.host_limit_input.fill(host_limit)
        view.details.host_limit_save_btn.click()

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

    def enable_repository(self, entity_name, repo_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.repository_sets.click()
        view.repository_sets.search(repo_name)
        view.repository_sets.check_box.click()
        view.repository_sets.actions.fill('Override to Enabled')


@navigator.register(ActivationKeyEntity, 'All')
class ShowAllActivationKeys(NavigateStep):
    """Navigate to All Activation Keys page"""

    VIEW = ActivationKeysView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle', 'Activation Keys')


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
