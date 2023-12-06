from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.capsule import (
    CapsuleDetailsView,
    CapsulesView,
    CreateCapsuleView,
    EditCapsuleView,
)


class CapsuleEntity(BaseEntity):
    endpoint_path = '/smart_proxies'

    def get_operation_status(self, view):
        """
        This functions accepts view and returns status of operation (success/error)
        or None if no message is displayed.

        Args:
            view (View): View of page where operation was performed
        Returns:
            refresh_status (str): Status of operation (success/error) or None
        """

        if view.success_message.is_displayed:
            refresh_status = view.success_message.read()
        elif view.error_message.is_displayed:
            refresh_status = view.error_message.read()
        else:
            refresh_status = None
        return refresh_status

    def read(self, capsule_name):
        """
        Read Capsule details from Capsules page

        Args:
            capsule_name (str): Name of capsule to be read
        """

        view = self.navigate_to(self, 'Capsules')
        view.searchbox.search(f'name="{capsule_name}"')
        return view.read()

    def read_details(self, capsule_name):
        """
        Read Capsule details from Capsule details page

        Args:
            capsule_name (str): Name of capsule to be read
        """

        view = self.navigate_to(self, 'Capsules')
        view.searchbox.search(f'name="{capsule_name}"')
        view.table.row(name=capsule_name)['Name'].click()
        view = CapsuleDetailsView(self.browser)
        return view.read()

    def read_all(self):
        """Read all values from Capsules page"""

        view = self.navigate_to(self, 'Capsules')
        return view.read()

    def view_documentation(self):
        """Opens Capsule documentation page"""

        view = self.navigate_to(self, 'Capsules')
        view.documentation.click()

    def create(self, values):
        """
        Function that creates capsule according to the parameters

        Args:
            values (dict): Dictionary of values to be filled in
            Structure of this dict should be:
            {
                'capsule.name': 'test',
                'capsule.url': 'test',
                'capsule.acs_http_proxy': 'test',
                'locations.resources.assigned': ['Default Location', 'test'],
                'organizations.resources.assigned': ['Default Organization', 'test'],
            }
        """

        view = self.navigate_to(self, 'Capsules')
        view.create_capsule.click()
        view = CreateCapsuleView(self.browser)
        view.fill(values)
        view.submit.click()
        view = CapsulesView(self.browser)

    def edit(
        self,
        capsule_name_to_edit,
        new_capsule_name=None,
        new_capsule_url=None,
        download_policy=None,
        acs_http_proxy=None,
        add_all_lces=False,
        remove_all_lces=False,
        assigned_lces=None,
        add_all_locations=False,
        remove_all_locations=False,
        assigned_locations=None,
        add_all_organizations=False,
        remove_all_organizations=False,
        assigned_organizations=None,
    ):
        """
        Function that edits capsule according to the parameters

        Args:
            capsule_name (str): Name of capsule to be edited
        """

        view = self.navigate_to(self, 'Capsules')
        view.search(f'name="{capsule_name_to_edit}"')
        view.table.row(name=capsule_name_to_edit)['Actions'].widget.fill('Edit')
        view = EditCapsuleView(self.browser)

        if new_capsule_name:
            view.capsule.name.fill(new_capsule_name)

        if new_capsule_url:
            view.capsule.url.fill(new_capsule_url)

        if download_policy:
            view.capsule.download_policy.fill(download_policy)

        if acs_http_proxy:
            view.capsule.acs_http_proxy.fill(acs_http_proxy)

        if acs_http_proxy is None and view.capsule.remove_proxy_selection.is_displayed:
            view.capsule.remove_proxy_selection.click()

        if add_all_lces:
            view.lifecycle_enviroments.resources.add_all()

        if remove_all_lces:
            view.lifecycle_enviroments.resources.remove_all()

        if assigned_lces:
            view.lifecycle_enviroments.resources.remove_all()
            view.lifecycle_enviroments.resources.fill({'assigned': assigned_lces})

        if add_all_locations:
            view.locations.resources.add_all()

        if remove_all_locations:
            view.locations.resources.remove_all()

        if assigned_locations:
            view.locations.resources.remove_all()
            view.locations.resources.fill({'assigned': assigned_locations})

        if add_all_organizations:
            view.organizations.resources.add_all()

        if remove_all_organizations:
            view.organizations.resources.remove_all()

        if assigned_organizations:
            view.organizations.resources.remove_all()
            view.organizations.resources.fill({'assigned': assigned_organizations})

        view.submit.click()
        view = CapsulesView(self.browser)
        view.search('')

    def refresh(self, capsule_name):
        """
        Function that refreshes given capsule

        Args:
            capsule_name (str): Name of capsule to be refreshed
        Returns:
            refresh_status (str): Status of refresh action (success/error) or None
        """

        view = self.navigate_to(self, 'Capsules')
        view.table.row(name=capsule_name)['Actions'].widget.fill('Refresh')

        return self.get_operation_status(view)

    def expire_logs(self, capsule_name):
        """
        Function that expires logs of given capsule

        Args:
            capsule_name (str): Name of capsule we want logs to expire
        """

        view = self.navigate_to(self, 'Capsules')
        view.table.row(name=capsule_name)['Actions'].widget.fill('Expire logs')

    def delete(self, capsule_name):
        """
        Delete given capsule

        Args:
            capsule_name (str): Name of capsule to be deleted
        Returns:
            refresh_status (str): Status of delete action (success/error) or None
        """

        view = self.navigate_to(self, 'Capsules')
        view.table.row(name=capsule_name)['Actions'].widget.fill('Delete')
        if view.confirm_deletion.is_displayed:
            view.confirm_deletion.confirm()

        return self.get_operation_status(view)

    def sync(self, capsule_name, sync_type):
        """
        General function for syncing capsule

        Args:
            capsule_name (str): Name of capsule to be synced
            sync_type (str): Type of sync to be performed
        """

        view = self.navigate_to(self, 'Capsules')
        view.searchbox.search(f'name="{capsule_name}"')
        view.table.row(name=capsule_name)['Name'].click()
        view = CapsuleDetailsView(self.browser)
        if sync_type == 'Optimized Sync':
            view.overview.synchronize_action_drop.fill(
                view.overview.synchronize_action_drop.items[0]
            )
        elif sync_type == 'Complete Sync':
            view.overview.synchronize_action_drop.fill(
                view.overview.synchronize_action_drop.items[1]
            )

    def optimized_sync(self, capsule_name):
        """
        Function that performs optimized sync of given capsule

        Args:
            capsule_name (str): Name of capsule to be synced
        """

        self.sync(capsule_name, 'Optimized Sync')

    def complete_sync(self, capsule_name):
        """
        Function that performs complete sync of given capsule

        Args:
            capsule_name (str): Name of capsule to be synced
        """

        self.sync(capsule_name, 'Complete Sync')

    def refresh_lce_counts(self, capsule_name, lce_name):
        """
        Function that refreshes LCE counts of given capsule

        Args:
            capsule_name (str): Name of capsule to be refreshed
        """

        view = self.navigate_to(self, 'Capsules')
        view.table.row(name=capsule_name)['Name'].click()
        view = CapsuleDetailsView(self.browser)
        view.content.top_content_table.row(Environment=lce_name)[3].widget.item_select(
            'Refresh counts'
        )


@navigator.register(CapsuleEntity, 'Capsules')
class OpenAcsPage(NavigateStep):
    """Navigate to the Capsules page"""

    VIEW = CapsulesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Capsules')
