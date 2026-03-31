from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStepWithWait as NavigateStep, navigator
from airgun.views.sync_status import SyncStatusView


class SyncStatusEntity(BaseEntity):
    endpoint_path = '/katello/sync_management'

    def read(self, widget_names=None, show_syncing_only=False):
        """Read all widgets at Sync status entity."""
        view = self.navigate_to(self, 'All')
        view.show_syncing_only.fill(show_syncing_only)
        return view.read(widget_names=widget_names)

    def synchronize(self, repository_paths, synchronous=True, timeout=3600):
        """Synchronize repositories

        :param repository_paths: A list of repositories to synchronize
            where each element of the list is path to repository represented
            by a list or tuple.
        :param synchronous: bool if to wait for all repos sync, defaults to True.
        :param timeout: time to wait for all repositories to be synchronized.

        Usage::

            synchronize([('product1', 'repo1'),
                         ('product1', 'repo2'),
                         ('product2', 'repo2'),
                         ('Red Hat Enterprise Linux Server', '7.5', 'x86_64',
                          'Red Hat Enterprise Linux 7 Server RPMs x86_64 7.5')])

        :return: the results text in Progress / Result columns
        """
        view = self.navigate_to(self, 'All')
        repo_rows = [view.table.get_node_from_path(repo_path) for repo_path in repository_paths]
        for repo_row in repo_rows:
            repo_row.select(True)
        view.synchronize.click()
        if synchronous:
            # Wait for sync to start (progress bars appear)
            wait_for(
                lambda: any(row.has_progress for row in repo_rows),
                timeout=60,
                delay=1,
                logger=view.logger,
            )
            # Wait for sync to finish (progress bars disappear)
            wait_for(
                lambda: all(not row.has_progress for row in repo_rows),
                timeout=timeout,
                delay=5,
                logger=view.logger,
            )

        return [row.result for row in repo_rows]


@navigator.register(SyncStatusEntity, 'All')
class ShowSyncStatus(NavigateStep):
    VIEW = SyncStatusView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Sync Status')
