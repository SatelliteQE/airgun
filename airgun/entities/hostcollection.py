import time

from navmazing import NavigateToSibling
from selenium.webdriver.common.by import By
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.hostcollection import (
    HostCollectionActionRemoteExecutionJobCreate,
    HostCollectionActionTaskDetailsView,
    HostCollectionChangeAssignedContentView,
    HostCollectionCreateView,
    HostCollectionEditView,
    HostCollectionInstallErrataView,
    HostCollectionManageModuleStreamsView,
    HostCollectionManagePackagesView,
    HostCollectionsView,
)
from airgun.views.job_invocation import JobInvocationCreateView, JobInvocationStatusView


class HostCollectionEntity(BaseEntity):
    endpoint_path = '/host_collections'

    def create(self, values):
        """Create a host collection"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete the host collection entity."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for 'value' and return host collections that match."""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Return a dict with properties of host collection."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update host collection properties with values."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.fill(values)

    def associate_host(self, entity_name, host_name):
        """Associate a host with host collection

        :param str entity_name: The host collection name.
        :param str host_name: The host name to be associated with to host
            collection name.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.hosts.resources.add(host_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def manage_packages(
        self,
        entity_name,
        content_type='Package',
        packages=None,
        action='install',
        action_via='via remote execution',
        job_values=None,
    ):
        """Manage host collection packages.

        :param str entity_name:  The host collection name.
        :param str content_type: The content type to apply action on.
            Available options: Package, Package Group.
        :param str packages: a list of packages separated by a space to apply
            the action on.
        :param str action: The action to apply. Available options: install,
            update, update_all, delete.
        :param str action_via: Via which mean to apply action. Available
            options: "via remote execution", "via remote execution - customize first"
        :param dict job_values: Remote Execution Job custom form values.
            When action_via is: "via remote execution - customize first",
            the new remote execution job form is opened and we can set custom
            values.
        """
        if job_values is None:
            job_values = {}
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.manage_packages.click()
        view = HostCollectionManagePackagesView(view.browser)
        if content_type is not None:
            view.content_type.fill(content_type)
        if packages is not None:
            view.packages.fill(packages)
        view.apply_action(action, action_via=action_via)
        view.flash.assert_no_error()
        view.flash.dismiss()
        if action_via == 'via remote execution - customize first':
            # After this step the user is redirected to remote execution job
            # create view.
            job_create_view = HostCollectionActionRemoteExecutionJobCreate(view.browser)
            self.browser.plugin.ensure_page_safe(timeout='5s')
            job_create_view.fill(job_values)
            submit = self.browser.selenium.find_element(By.XPATH, './/input[@value="Submit"]')
            submit.click()

        # wait for the job deatils to load
        time.sleep(3)
        # After this step the user is redirected to job status view.
        job_status_view = JobInvocationStatusView(view.browser)
        wait_for(
            lambda: (
                job_status_view.overview.job_status.read() != 'Pending'
                and job_status_view.overview.job_status_progress.read() == '100%'
            ),
            timeout=300,
            delay=10,
            logger=view.logger,
        )
        return job_status_view.overview.read()

    def search_applicable_hosts(self, entity_name, errata_id):
        """Check for search URI in Host Collection errata view.

        :param str entity_name:  The host collection name.
        :param str errata_id: the applicable errata id.

        :return: Search URL to list the applicable hosts
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.install_errata.click()
        view = HostCollectionInstallErrataView(view.browser)
        uri = view.search_url.__element__().get_attribute('href')
        self.browser.handle_alert()
        return uri

    def install_errata(
        self, entity_name, errata_id, install_via='via remote execution', job_values=None
    ):
        """Install host collection errata

        :param str entity_name:  The host collection name.
        :param str errata_id: the errata id to install.
        :param str install_via: Via which mean to install errata. Available
            options: "via remote execution", "via remote execution - customize first"
        :param dict job_values: Remote Execution Job custom form values.
            When install_via is: "via remote execution - customize first",
            the new remote execution job form is opened and we can set custom
            values.
        :return: Job status view values.
        """
        if job_values is None:
            job_values = {}
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.install_errata.click()
        view = HostCollectionInstallErrataView(view.browser)
        view.search.fill(errata_id)
        view.table.row(Id=errata_id)[0].widget.fill(True)
        view.install.fill(install_via)
        if view.dialog.is_displayed:
            self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()
        if install_via == 'via remote execution - customize first':
            # After this step the user is redirected to remote execution job
            # create view.
            job_create_view = HostCollectionActionRemoteExecutionJobCreate(view.browser)
            job_create_view.fill(job_values)
            job_create_view.submit.click()

        # After this step the user is redirected to job status view.
        job_status_view = JobInvocationStatusView(view.browser)
        wait_for(
            lambda: (
                job_status_view.overview.job_status.read() != 'Pending'
                and job_status_view.overview.job_status_progress.read() == '100%'
            ),
            timeout=300,
            delay=10,
            logger=view.logger,
        )
        return job_status_view.overview.read()

    def manage_module_streams(
        self,
        entity_name,
        action_type,
        module_name,
        stream_version,
        customize=False,
        customize_values=None,
    ):
        """Manage module streams
        :param str entity_name:  The host collection name.
        :param action_type: remote action to execute on content host. Action value can be one of
        them e.g. 'Enable', 'Disable', 'Install', 'Update', 'Remove', 'Reset'

        :param str module_name: Module Stream name to remotely
            install/upgrade/remove (depending on `action_type`)
        :param str stream_version:  String with Stream Version of Module
        :param customize: Boolean indicating if additional custom action should be called
        :param customize_values: Dict with custom actions to run. Mandatory if customize is True

        :return: Returns a dict containing job status details
        """
        if customize_values is None:
            customize_values = {}
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.manage_module_streams.click()
        view = HostCollectionManageModuleStreamsView(view.browser)
        view.search(f'name = {module_name} and stream = {stream_version}')
        action_type = {'is_customize': customize, 'action': action_type}
        view.table.row(name=module_name, stream=stream_version)['Actions'].fill(action_type)
        if customize:
            view = JobInvocationCreateView(view.browser)
            view.fill(customize_values)
            view.submit.click()
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()
        return view.read()

    def change_assigned_content(self, entity_name, lce, content_view):
        """Change host collection lifecycle environment and content view

        :param str entity_name:  The host collection name.
        :param str lce:  Lifecycle environment name.
        :param str content_view:  Content view name.
        :return: task details view values
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.change_assigned_content.click()
        view = HostCollectionChangeAssignedContentView(view.browser)
        view.lce.fill({lce: True})
        view.content_view.fill(content_view)
        view.assign.click()
        view.dialog.confirm_dialog.click()
        task_view = HostCollectionActionTaskDetailsView(view.browser)
        task_view.progressbar.wait_for_result()
        return task_view.read()


@navigator.register(HostCollectionEntity, 'All')
class ShowAllHostCollections(NavigateStep):
    VIEW = HostCollectionsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Host Collections')


@navigator.register(HostCollectionEntity, 'New')
class AddNewHostCollections(NavigateStep):
    VIEW = HostCollectionCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HostCollectionEntity, 'Edit')
class EditHostCollections(NavigateStep):
    VIEW = HostCollectionEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
