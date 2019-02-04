from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.subscription import (
    AddSubscriptionView,
    DeleteManifestConfirmationView,
    ManageManifestView,
    SubscriptionDetailsView,
    SubscriptionListView,
)


class SubscriptionEntity(BaseEntity):
    def _wait_for_process_to_finish(self, name, has_manifest=False, timeout=600,
                                    ignore_error_messages=None):
        """Helper ensuring that task (upload / delete manifest / subscription)
        has finished. Run after action invoking task to leave Satellite
        in usable state.
        Currently waits for three events. Since page is written asynchronously,
        they can happen in any order.
        :param name: Name of running task
        :param has_manifest: Should manifest exist after task ended?
        :param timeout: Waiting timeout
        :param ignore_error_messages: A List of strings representing the error messages to ignore.
        """
        view = SubscriptionListView(self.browser, logger=self.browser.logger)
        wait_for(
                lambda: not view.progressbar.is_displayed,
                handle_exception=True, timeout=timeout,
                logger=view.progressbar.logger
        )
        wait_for(
                lambda: self.has_manifest == has_manifest,
                handle_exception=True, timeout=10,
                logger=view.logger
        )
        view.flash.assert_no_error(ignore_messages=ignore_error_messages)
        view.flash.dismiss()

    @property
    def has_manifest(self):
        """Is there manifest present in current organization?
        :return: boolean value indicating whether manifest is present
        """
        view = self.navigate_to(self, 'All')
        return not view.add_button.disabled

    def add_manifest(self, manifest_file, ignore_error_messages=None):
        """Upload manifest file
        :param manifest_file: Path to manifest file
        :param ignore_error_messages: List of error messages to ignore
        """
        view = self.navigate_to(self, 'Manage Manifest')
        view.wait_animation_end()
        view.manifest.manifest_file.fill(manifest_file)
        self._wait_for_process_to_finish(
            'Import Manifest', has_manifest=True, ignore_error_messages=ignore_error_messages)

    def refresh_manifest(self):
        """Refresh manifest"""
        view = self.navigate_to(self, 'Manage Manifest')
        view.wait_animation_end()
        view.manifest.refresh_button.click()
        org_name = view.taxonomies.current_org
        self._wait_for_process_to_finish(
            'Refresh Manifest organization \'{}\''.format(org_name),
            has_manifest=True,
            timeout=1200
        )

    def delete_manifest(self, ignore_error_messages=None):
        """Delete manifest from current organization"""
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        view.wait_animation_end()
        view.delete_button.click()
        self._wait_for_process_to_finish(
            'Delete Manifest', has_manifest=False, ignore_error_messages=ignore_error_messages)

    def read_delete_manifest_message(self):
        """Read message displayed on 'Confirm delete manifest' dialog"""
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        view.wait_animation_end()
        delete_message = view.message.read()
        # To not break further navigation, we need to close all the opened modal dialogs views
        view.cancel_button.click()
        manage_view = ManageManifestView(self.browser)
        if manage_view.is_displayed:
            manage_view.close_button.click()
        return delete_message

    def add(self, entity_name, quantity=1):
        """Attach new subscriptions
        :param entity_name: Name of subscription to attach
        :param quantity: Number of subscriptions to attach
        """
        view = self.navigate_to(self, 'Add')
        for row in view.table.rows(subscription_name=entity_name):
            row['Quantity to Allocate'].fill(quantity)
        view.submit_button.click()
        self._wait_for_process_to_finish(
                'Bind entitlements to an allocation', has_manifest=True)

    def search(self, value):
        """search for subscription"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def filter_columns(self, columns=None):
        """Filters column headers
        :param columns: dict mapping column name to boolean value
        :return: tuple of the name of the headers
        """
        view = self.navigate_to(self, 'All')
        if columns is not None:
            view.columns_filter_checkboxes.fill(columns)
            wait_for(
                lambda: view.table.headers is not None,
                timeout=10,
                delay=1,
                handle_exception=True,
                logger=view.logger
            )
        return view.table.headers

    def provided_products(self, entity_name, virt_who=False):
        """Read list of all products provided by subscription.
        :param entity_name: Name of subscription
        :param virt_who: Whether this is a virt who client subscription.
        :return: List of strings with product names
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name, virt_who=virt_who)
        return view.details.provided_products.read()

    def content_products(self, entity_name, virt_who=False):
        """Read list of products provided by subscription for subscribed content hosts.
        :param entity_name: Name of subscription
        :param virt_who: Whether this is a virt who client subscription.
        :return: List of strings with product names (may be empty)
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name, virt_who=virt_who)
        view.product_content.select()
        return view.product_content.product_content_list.read()

    def update(self, entity_name, values):
        """Stub method provided for consistency with other Airgun entities.
        This operation was never implemented in Robottelo (no test requires
        it).
        """
        raise NotImplementedError("Subscriptions update is not implemented")

    def delete(self, entity_name):
        """Remove subscription
        :param entity_name: Name of subscription
        """
        view = self.navigate_to(self, 'All')
        for row in view.table.rows(name=entity_name):
            row['Select all rows'].fill(True)
        view.delete_button.click()
        view.confirm_deletion.confirm()
        self._wait_for_process_to_finish(
                'Delete Upstream Subscription', has_manifest=True)


class SubscriptionNavigationStep(NavigateStep):
    """To ensure that we reached the destination, some targets need extra post navigation tasks"""

    def post_navigate(self, _tries, *args, **kwargs):
        wait_for(
            lambda: self.am_i_here(*args, **kwargs),
            timeout=30,
            delay=1,
            handle_exception=True,
            logger=self.view.logger
        )


@navigator.register(SubscriptionEntity, 'All')
class SubscriptionList(SubscriptionNavigationStep):
    """Navigate to Subscriptions main page"""
    VIEW = SubscriptionListView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Subscriptions')


@navigator.register(SubscriptionEntity, 'Manage Manifest')
class ManageManifest(NavigateStep):
    """Navigate to 'Manage Manifest' dialog box on Subscriptions main page"""
    VIEW = ManageManifestView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.manage_manifest_button.click()


@navigator.register(SubscriptionEntity, 'Delete Manifest Confirmation')
class DeleteManifestConfirmation(NavigateStep):
    """Navigate to 'Delete Manifest Confirmation' dialog box on
    Subscriptions main page
    Dialog box appearance is animated. wait_for ensures that we
    interact with content only after animation has finished
    """
    VIEW = DeleteManifestConfirmationView

    prerequisite = NavigateToSibling('Manage Manifest')

    def step(self, *args, **kwargs):
        wait_for(
                lambda: not self.parent.manifest.delete_button.disabled,
                handle_exception=True, logger=self.view.logger, timeout=10
        )
        self.parent.manifest.delete_button.click()


@navigator.register(SubscriptionEntity, 'Add')
class AddSubscription(NavigateStep):
    """Navigate to Add Subscriptions page"""
    VIEW = AddSubscriptionView

    prerequisite = NavigateToSibling('All')

    def am_i_here(self, *args, **kwargs):
        return (self.view.is_displayed
                and self.view.breadcrumb.locations[1] == 'Add Subscriptions')

    def step(self, *args, **kwargs):
        self.parent.add_button.click()


@navigator.register(SubscriptionEntity, 'Details')
class SubscriptionDetails(SubscriptionNavigationStep):
    """Navigate to Subscriptions' Details page

    Args:
        entity_name: name of Subscription
        virt_who: Whether this is a virt who client subscription.
    """
    VIEW = SubscriptionDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        subscription_name = kwargs.get('entity_name')
        virt_who = kwargs.get('virt_who')
        search_string = 'name = "{0}"'.format(subscription_name)
        if virt_who:
            search_string = 'virt_who = true and {0}'.format(search_string)
        self.parent.search(search_string)
        self.parent.table.row(name=subscription_name)['Name'].widget.click()
