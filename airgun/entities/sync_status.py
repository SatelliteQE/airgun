from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.sync_status import SyncStatusView


class SyncStatusEntity(BaseEntity):
    endpoint_path = "/katello/sync_management"

    def read(self, widget_names=None, active_only=False):
        """Read all widgets at Sync status entity"""
        view = self.navigate_to(self, "All")
        view.active_only.fill(active_only)
        return view.read(widget_names=widget_names)

    def synchronize(self, repository_paths, synchronous=True, timeout=3600):
        """Synchronize repositories

        :param repository_paths: A list of repositories to synchronize
            where each element of the list is path to repository represented by a list or tuple.
        :param synchrounous: bool if to wait for all repos sync, defaults to True.
        :param timeout: time to wait for all repositories to be synchronized.

        Usage::

            synchronize([('product1', 'repo1'),
                         ('product1', 'repo2'),
                         ('product2', 'repo2'),
                         ('Red Hat Enterprise Linux Server', '7.5', 'x86_64',
                          'Red Hat Enterprise Linux 7 Server RPMs x86_64 7.5'),
                         ('Red Hat Satellite Capsule',
                          'Red Hat Satellite Capsule 6.2 for RHEL 7 Server RPMs x86_64')])

        :return: the results text in RESULT columns
        """
        view = self.navigate_to(self, "All")
        repo_nodes = [
            view.table.get_node_from_path(repo_path) for repo_path in repository_paths
        ]
        for repo_node in repo_nodes:
            repo_node.fill(True)
        view.synchronize_now.click()
        if synchronous:
            wait_for(
                lambda: all(node.progress is None for node in repo_nodes),
                timeout=timeout,
                delay=5,
                logger=view.logger,
            )

        return [node.result for node in repo_nodes]


@navigator.register(SyncStatusEntity, "All")
class ShowAllHostCollections(NavigateStep):
    VIEW = SyncStatusView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select("Content", "Sync Status")
