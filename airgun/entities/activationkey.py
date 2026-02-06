import time
from wait_for import wait_for
from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.activationkey import (
    ActivationKeyCreateView,
    ActivationKeyEditView,
    ActivationKeysView,
)
from airgun.views.host_new import ManageMultiCVEnvModal


class ActivationKeyEntity(BaseEntity):
    endpoint_path = '/activation_keys'

    def create(self, values):
        """Create new activation key entity"""
        view = self.navigate_to(self, 'New')
        view.wait_displayed()
        basic_fields = {k: v for k, v in values.items() if k not in ['lce', 'content_view']}
        if basic_fields:
            view.fill(basic_fields)
        if 'lce' in values or 'content_view' in values:
            lce_dict = values.get('lce', {})
            cv_name = values.get('content_view')
            view.assign_cv_env_btn.click()
            time.sleep(3)
            self._update_cv_lce_via_modal(lce_dict, cv_name)
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
        view.wait_displayed(timeout='10s')
        return view.read(widget_names=widget_names)

    def get_repos(self, entity_name, repo_type='All'):
        """Read all values for repository sets on activation keys"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.repository_sets.repo_type.select_by_visible_text(repo_type)
        return view.repository_sets.table.read()

    def update(self, entity_name, values):
        """Update necessary values for activation key

        Handles both formats:
        - Nested: {'details': {'lce': {env: True}, 'content_view': cv}}
        - Dot-notation: {'details.lce': {env: True}, 'details.content_view': cv}
        """
        # Check for dot-notation format and convert to nested if needed
        lce_update = None
        cv_update = None

        if 'details.lce' in values:
            lce_update = values.pop('details.lce')
        if 'details.content_view' in values:
            cv_update = values.pop('details.content_view')

        if 'details' in values and isinstance(values['details'], dict):
            if 'lce' in values['details']:
                lce_update = values['details'].pop('lce')
            if 'content_view' in values['details']:
                cv_update = values['details'].pop('content_view')
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.wait_displayed()
        if lce_update and not cv_update:
            cv_details = view.details.content_view_details.read()
            if cv_details and len(cv_details) > 0:
                current_cv = cv_details[0]['content_view']
                if current_cv:
                    cv_update = current_cv
        # Update other fields first if any remain
        if values:
            view.fill(values)
            view.flash.assert_no_error()
            view.flash.dismiss()

        # Update LCE/CV via modal if provided
        if lce_update or cv_update:
            view.details.content_view_details.dropdown.item_select('Assign content view environments')
            self._update_cv_lce_via_modal(lce_update, cv_update)

    def _update_cv_lce_via_modal(self, lce_dict, cv_name):
        """Helper to update CV/LCE using the modal pattern

        Args:
            lce_dict: Dictionary like {env_name: True} for LCE selection
            cv_name: String with content view name
        """
        modal = ManageMultiCVEnvModal(self.browser)
        modal.wait_displayed()
        lce_name = lce_dict
        if isinstance(lce_dict, dict):
            lce_name = next((k for k, v in lce_dict.items() if v), None)

        if lce_name and cv_name:
            assignment_section = modal.new_assignment_section(lce_name=lce_name)
            assignment_section.lce_selector.click()
            assignment_section.content_source_select.item_select(cv_name)

        modal.save_btn.click()
        wait_for(
            lambda: not modal.is_displayed,
            timeout=10,
            delay=1,
            handle_exception=True,
        )

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
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
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

    @retry_navigation
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
