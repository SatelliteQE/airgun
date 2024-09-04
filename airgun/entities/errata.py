from airgun import ERRATA_REGEXP
from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.errata import (
    ErrataDetailsView,
    ErrataInstallationConfirmationView,
    ErratumView,
)
from airgun.views.job_invocation import JobInvocationStatusView


class ErrataEntity(BaseEntity):
    endpoint_path = '/errata'

    def search(self, value, applicable=True, installable=False, repo=None):
        """Search for specific errata.

        :param str value: search query to type into search field.
        :param bool applicable: filter by only applicable errata
        :param bool installable: filter by only installable errata
        :param str optional repo: filter by repository name
        :return: list of dicts representing table rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        return view.search(value, applicable=applicable, installable=installable, repo=repo)

    def read(
        self,
        entity_name,
        applicable=False,
        installable=False,
        repo=None,
        environment=None,
        widget_names=None,
    ):
        """Read errata details.

        :param str entity_name: errata id or title
        :param bool applicable: filter by only applicable errata
        :param bool installable: filter by only installable errata
        :param str optional repo: filter by repository name
        :param str optional environment: filter applicable hosts by environment
            name
        :return: dict representing tabs, with nested dicts representing fields
            and values
        :rtype: dict
        """
        view = self.navigate_to(
            self,
            'Details',
            entity_name=entity_name,
            applicable=applicable,
            installable=installable,
            repo=repo,
        )
        if environment:
            view.content_hosts.environment_filter.fill(environment)
        return view.read(widget_names=widget_names)

    def install(self, entity_name, host_names, environment=None):
        """Install errata on content host.

        :param str entity_name: errata id or title
        :param str host_names: content host name to apply errata on.
            pass a single str hostname,
            or pass 'All' for any available hosts,
            or pass a list of str hostnames.
        :param str environment: name of lifecycle environment to scope errata.
            default: None
        """
        view = self.navigate_to(
            self,
            'Details',
            entity_name=entity_name,
            applicable=False,
            installable=False,
            repo=None,
        )
        if environment:
            view.content_hosts.environment_filter.fill(environment)
        view.content_hosts.wait_displayed()

        if host_names == 'All':
            # select_all on table, check if single or multiple hosts
            view.content_hosts.select_all.fill(True)
        elif isinstance(host_names, list):
            # find and select hostnames in table from list
            for hostname in host_names:
                view.content_hosts.table.row(name=hostname)[0].fill(True)
        else:
            # search and select the single passed hostname
            view.content_hosts.search(host_names)
            view.content_hosts.wait_displayed()
            view.content_hosts.table.row(name=host_names)[0].fill(True)
        view.content_hosts.wait_displayed()
        view.content_hosts.apply.click()
        # brought to confirmation page
        view = ErrataInstallationConfirmationView(view.browser)
        view.wait_displayed()
        view.confirm.click()
        # wait for redirect to task details page
        view = JobInvocationStatusView(view.browser)
        view.wait_for_result(delay=0.01, timeout=1200)
        return view.read()

    def search_content_hosts(self, entity_name, value, environment=None):
        """Search errata applicability for content hosts.

        :param str entity_name: errata id or title
        :param str value: search query to type into search field.
        :param str optional environment: filter applicable hosts by environment name
        """
        view = self.navigate_to(
            self,
            'Details',
            entity_name=entity_name,
            applicable=False,
            installable=False,
            repo=None,
        )
        view.content_hosts.wait_displayed()
        return view.content_hosts.search(value, environment=environment)


@navigator.register(ErrataEntity, 'All')
class ShowAllErratum(NavigateStep):
    """Navigate to All Erratum screen."""

    VIEW = ErratumView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Types', 'Errata')


@navigator.register(ErrataEntity, 'Details')
class ErrataDetails(NavigateStep):
    """Navigate to Errata details page.

    Args:
        entity_name: id or title of errata

    Optional Args:
        applicable: whether to filter errata by only applicable ones
        installable: whether to filter errata by only installable ones
        repo: name of repository to filter errata by
    """

    VIEW = ErrataDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        applicable = kwargs.get('applicable')
        installable = kwargs.get('installable')
        repo = kwargs.get('repo')
        self.parent.search(entity_name, applicable=applicable, installable=installable, repo=repo)
        row_filter = {'title': entity_name}
        if ERRATA_REGEXP.search(entity_name):
            row_filter = {'errata_id': entity_name}
        self.parent.table.row(**row_filter)['Errata ID'].widget.click()
