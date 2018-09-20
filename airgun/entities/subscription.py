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
    def _wait_for_process_to_finish(self, has_manifest=False):
        view = self.navigate_to(self, 'All')
        view.progressbar.wait_displayed(timeout=20)
        wait_for(
                lambda: not view.progressbar.is_displayed,
                timeout=60*10,
                logger=view.progressbar.logger
        )
        wait_for(
                lambda: self.has_manifest == has_manifest,
                timeout=10,
                logger=view.progressbar.logger
        )
        view.flash.dismiss()

    @property
    def has_manifest(self):
        view = self.navigate_to(self, 'All')
        return "disabled" not in view.browser.classes(view.add_button)

    def add_manifest(self, manifest_file):
        view = self.navigate_to(self, 'Manage Manifest')
        view.fill({
            'manifest.manifest_file': manifest_file,
        })
        self._wait_for_process_to_finish(has_manifest=True)

    def delete_manifest(self):
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        view.delete_button.click()
        self._wait_for_process_to_finish(has_manifest=False)

    def read_delete_manifest_message(self):
        view = self.navigate_to(self, 'Delete Manifest Confirmation')
        return view.message.read()

    def add(self, entity_name, quantity=1):
        view = self.navigate_to(self, 'Add')
        for row in view.table.rows(subscription_name=entity_name):
            row['Quantity to Allocate'].fill(quantity)
        view.submit_button.click()
        self._wait_for_process_to_finish(has_manifest=True)

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def provided_products(self, entity_name):
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        return view.details.provided_products

    def enabled_products(self, entity_name):
        view = self.navigate_to(self, 'Details', entity_name=entity_name)
        view.enabled_products.select()
        return view.enabled_products.enabled_products_list

    def update(self, entity_name, values):
        # This operation was never implemented in Robottelo (no test
        # requires it). It is here for consistency, but raises
        # exception until it is actually needed
        raise NotImplementedError("Subscriptions update is not implemented")

    def delete(self, entity_name):
        view = self.navigate_to(self, 'All')
        for row in view.table.rows(name=entity_name):
            row['Select all rows'].fill(True)
        view.delete_button.click()
        view.confirm_deletion.confirm()
        self._wait_for_process_to_finish(has_manifest=True)


@navigator.register(SubscriptionEntity, 'All')
class SubscriptionList(NavigateStep):
    VIEW = SubscriptionListView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Subscriptions')


@navigator.register(SubscriptionEntity, 'Manage Manifest')
class ManageManifest(NavigateStep):
    VIEW = ManageManifestView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.manage_manifest_button.click()

    def post_navigate(self, _tries, *args, **kwargs):
        return self.view.is_displayed


@navigator.register(SubscriptionEntity, 'Delete Manifest Confirmation')
class DeleteManifestConfirmation(NavigateStep):
    VIEW = DeleteManifestConfirmationView

    prerequisite = NavigateToSibling('Manage Manifest')

    def step(self, *args, **kwargs):
        wait_for(
                lambda: not self.parent.manifest.delete_button.disabled,
                logger=self.view.logger,
                timeout=10
        )
        self.parent.manifest.delete_button.click()

    def post_navigate(self, _tries, *args, **kwargs):
        return self.view.is_displayed


@navigator.register(SubscriptionEntity, 'Add')
class AddSubscription(NavigateStep):
    VIEW = AddSubscriptionView

    prerequisite = NavigateToSibling('All')

    def am_i_here(self, *args, **kwargs):
        return (self.view.is_displayed
                and self.view.breadcrumb.locations[1] == 'Add Subscriptions')

    def step(self, *args, **kwargs):
        self.parent.add_button.click()


@navigator.register(SubscriptionEntity, 'Details')
class SubscriptionDetails(NavigateStep):
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
