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
    def _wait_for_process_to_finish(self, name, has_manifest=False, timeout=600):
        """Helper ensuring that task (upload / delete manifest / subscription)
        has finished. Run after action invoking task to leave Satellite
        in usable state.
        Currently waits for three events. Since page is written asynchronously,
        they can happen in any order.
        :param name: Name of running task
        :param has_manifest: Should manifest exist after task ended?
        """
        view = SubscriptionListView(self.browser, logger=self.browser.logger)
        wait_for(
                lambda: view.flash.assert_message(
                        "Task {} completed".format(name), partial=True),
                handle_exception=True, timeout=timeout,
                logger=view.flash.logger
        )
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
        # uncomment when BZ#1651981 is fixed
        # view.flash.assert_no_error()
        view.flash.dismiss()

    @property
    def has_manifest(self):
        """Is there manifest present in current organization?
        :return: boolean value indicating whether manifest is present
        """
        view = self.navigate_to(self, 'All')
        return not view.add_button.disabled

    def add_manifest(self, manifest_file):
        """Upload manifest file
        :param manifest_file: Path to manifest file
        """
        view = self.navigate_to(self, 'Manage Manifest')
        view.wait_animation_end()
        view.fill({
            'manifest.manifest_file': manifest_file,
        })
        self._wait_for_process_to_finish('Import Manifest', has_manifest=True)

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

    def delete_manifest(self):
        """Delete manifest from current organization"""
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        view.wait_animation_end()
        view.delete_button.click()
        self._wait_for_process_to_finish('Delete Manifest', has_manifest=False)

    def read_delete_manifest_message(self):
        """Read message displayed on 'Confirm delete manifest' dialog"""
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        view.wait_animation_end()
        return view.message.read()

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

    def provided_products(self, entity_name):
        """Read list of products provided by subscription
        :param entity_name: Name of subscription
        :return: List of strings with product names
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.details.provided_products.read()

    def enabled_products(self, entity_name):
        """Read list of enabled products provided by subscription
        Catches possible exception to always return known data structure
        :param entity_name: Name of subscription
        :return: List of strings with product names (may be empty)
        """
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.enabled_products.select()
        return view.enabled_products.enabled_products_list.read()

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


@navigator.register(SubscriptionEntity, 'All')
class SubscriptionList(NavigateStep):
    """Navigate to Subscriptions main page"""
    VIEW = SubscriptionListView

    def pre_navigate(self, _tries, *args, **kwargs):
        super(SubscriptionList, self).pre_navigate(_tries, *args, **kwargs)
        wait_for(
                lambda: not self.view.fake_fade_widget.is_displayed,
                handle_exception=True, logger=self.view.logger, timeout=10 * 60
        )

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
class SubscriptionDetails(NavigateStep):
    """Navigate to Subscriptions' Details page

    Args:
        entity_name: name of Subscription
    """
    VIEW = SubscriptionDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def am_i_here(self, *args, **kwargs):
        subscription_name = kwargs.get('subscription')
        return (self.view.is_displayed and
                self.view.breadcrumb.read() == subscription_name)

    def step(self, *args, **kwargs):
        subscription_name = kwargs.get('entity_name')
        self.parent.table.row(name=subscription_name)['Name'].widget.click()
