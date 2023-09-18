from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.contenthost import (
    ContentHostDetailsView,
    ContentHostsView,
    ContentHostTaskDetailsView,
    ErrataDetailsView,
    SyspurposeBulkActionView,
)
from airgun.views.host_new import NewHostDetailsView
from airgun.views.job_invocation import JobInvocationCreateView, JobInvocationStatusView


class ContentHostEntity(BaseEntity):
    endpoint_path = '/content_hosts'

    def delete(self, entity_name):
        """Delete existing content host"""
        view = self.navigate_to(self, 'All')
        view.search(entity_name)
        view.table.row(name=entity_name)[0].widget.fill(True)
        view.actions.fill('Delete Hosts')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific content host"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read_all(self, widget_names=None):
        """Read all values from content host title page.
        Optionally, read only the widgets in widget_names.
        """
        view = self.navigate_to(self, 'All')
        return view.read(widget_names=widget_names)

    def read(self, entity_name, widget_names=None):
        """Read content host details, optionally read only the widgets in widget_names."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def read_legacy_ui(self, entity_name, widget_names=None):
        """Read host values from Host Details page, optionally only the widgets in widget_names
        will be read.
        """
        view = self.navigate_to(self, 'LegacyDetails', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def execute_package_action(self, entity_name, action_type, value, installed_via='rex'):
        """Execute remote package action on a content host.

        The installation method is not set here, but the path changes according to the method used.
        For katello-agent, the Content Hosts' Task tab displays the progress. If REX is used,
        the Job Invocation view displays the progress. In 6.10, REX became the default method.

        :param entity_name: content host name to remotely execute package
            action on
        :param action_type: remote action to execute. Can be one of 5: 'Package
            Install', 'Package Update', 'Package Remove', 'Group Install' or
            'Group Remove'
        :param value: Package or package group group name to remotely
            install/upgrade/remove (depending on `action_type`)

        :param installed_via: what installation method was used (REX or katello-agent)

        :return: Returns a dict containing task status details
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.packages_actions.action_type.fill(action_type)
        view.packages_actions.name.fill(value)
        view.packages_actions.perform.click()
        if installed_via == 'katello':
            view = ContentHostTaskDetailsView(view.browser)
            view.progressbar.wait_for_result()
        else:
            view = JobInvocationStatusView(view.browser)
            view.wait_for_result()
        return view.read()

    def bulk_set_syspurpose(self, hosts, values):
        """Set system purpose for multiple hosts"""
        view = self.navigate_to(self, 'All')
        view.search(' or '.join(hosts))
        view.select_all.fill(True)
        view.actions.fill('Manage System Purpose')
        view = SyspurposeBulkActionView(view.browser)
        view.fill(values)
        self.browser.click(view.assign)

    def execute_module_stream_action(
        self,
        entity_name,
        action_type,
        module_name,
        stream_version,
        customize=False,
        customize_values=None,
    ):
        """Execute remote module_stream action on a content

        :param entity_name: content host name
        :param action_type: remote action to execute on content host. Action value can be one of
            them e.g. 'Enable', 'Disable', 'Install', 'Update', 'Remove', 'Reset'
        :param module_name: Module Stream name to remotely
            install/upgrade/remove (depending on `action_type`)
        :param stream_version: String with Stream Version of Module
        :param customize: Boolean indicating if additional custom action should be called
        :param customize_values: Dict with custom actions to run. Mandatory if customize is True

        :return: Returns a dict containing job status details
        """
        if customize_values is None:
            customize_values = {}
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.module_streams.search(f'name = {module_name} and stream = {stream_version}')
        action_type = {'is_customize': customize, 'action': action_type}
        view.module_streams.table.row(name=module_name, stream=stream_version)['Actions'].fill(
            action_type
        )
        if customize:
            view = JobInvocationCreateView(view.browser)
            view.fill(customize_values)
            view.submit.click()
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result()
        return view.read()

    def search_package(self, entity_name, package_name):
        """Search for specific package installed in content host"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.packages_installed.search(package_name)
        return view.packages_installed.table.read()

    def search_module_stream(self, entity_name, module_name, stream_version=None, status='All'):
        """Search for specific package installed in content host"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        if stream_version is None:
            query = module_name
        else:
            query = f'name = {module_name} and stream = {stream_version}'
        view.module_streams.search(query, status)
        return view.module_streams.table.read()

    def install_errata(self, entity_name, errata_id, install_via=None):
        """Install errata on a content host

        :param name: content host name to apply errata on
        :param errata_id: errata id or title, e.g. 'RHEA-2012:0055'
        :param str install_via: via which mean to install errata. Available
            options: "katello", "rex", "rex_customize"

        :return: Returns a dict containing task status details
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        if errata_id == "All":
            view.errata.select_all.fill(True)
        else:
            view.errata.search(errata_id)
            view.errata.table.row(id=errata_id)[0].widget.fill(True)
        install_via_dict = {
            'katello': 'via Katello agent',
            'rex': 'via remote execution',
            'rex_customize': 'via remote execution - customize first',
        }
        view.errata.apply_selected.fill(install_via_dict[install_via])
        if install_via == 'katello':
            view = ContentHostTaskDetailsView(view.browser)
            view.progressbar.wait_for_result()
        else:
            view = JobInvocationStatusView(view.browser)
            view.wait_for_result()
        return view.read()

    def search_errata(self, entity_name, errata_id, environment=None):
        """Search for specific errata applicable for content host.

        :param str entity_name: the content hosts name.
        :param str errata_id: errata id or title, e.g. 'RHEA-2012:0055'
        :param str optional environment: lifecycle environment to filter by.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.errata.search(errata_id, lce=environment)
        return view.errata.table.read()

    def read_errata_details(self, entity_name, errata_id, environment=None):
        """Read Details for specific errata applicable for content host.

        :param str entity_name: the content hosts name.
        :param str errata_id: errata id or title, e.g. 'RHEA-2012:0055'
        :param str optional environment: lifecycle environment to filter by.
        """
        view = self.navigate_to(
            self,
            'Errata Details',
            entity_name=entity_name,
            errata_id=errata_id,
            environment=environment,
        )
        return view.read()

    def export(self):
        """Export content hosts list.

        :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        view.export.click()
        return self.browser.save_downloaded_file()

    def add_subscription(self, entity_name, subscription_name):
        """Add a subscription to content host.

        :param str entity_name: the content hosts name.
        :param str subscription_name: The subscription name to add to content host.
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.subscriptions.resources.add(subscription_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def update(self, entity_name, values):
        """Update content host values."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(ContentHostEntity, 'All')
class ShowAllContentHosts(NavigateStep):
    """Navigate to All Content Hosts screen."""

    VIEW = ContentHostsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Content Hosts')


@navigator.register(ContentHostEntity, 'Edit')
class EditContentHost(NavigateStep):
    """Navigate to Content Host details screen.

    Args:
        entity_name: name of content host
    """

    VIEW = ContentHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(ContentHostEntity, 'Errata Details')
class NavigateToErrataDetails(NavigateStep):
    """Navigate to Errata details screen.

    Args:
        entity_name: name of content host
        errata_id: id of errata
    """

    VIEW = ErrataDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        errata_id = kwargs.get('errata_id')
        environment = kwargs.get('environment')
        self.parent.errata.search(errata_id, lce=environment)
        self.parent.errata.table.row(id=errata_id)['Id'].widget.click()


@navigator.register(ContentHostEntity, 'LegacyDetails')
class ShowContentHostDetails(NavigateStep):
    """Navigate to Host Details page by clicking on necessary host name in the
    table

    Args:
        entity_name: name of the host
    """

    VIEW = ContentHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
        host_view = NewHostDetailsView(self.parent.browser)
        host_view.wait_displayed()
        host_view.dropdown.wait_displayed()
        host_view.dropdown.item_select('Legacy content host UI')
