from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.ansible_collections import AnsibleCollectionsView
from airgun.views.ansible_collections import AnsibleCollectionsDetailsView


class AnsibleCollectionsEntity(BaseEntity):
    endpoint_path = '/ansible_collections'

    def search(self, query):
        """Search for ansible collection
        :param str query: search query to type into search field. E.g.
            ``name = "ant"``.
        """
        view = self.navigate_to(self, 'All')
        return view.search(query)

    def read(self, collection_name, collection_version, widget_names=None):
        """Read collection values from Ansible Collections Details page
        :param str collection_name: the collection name to read.
        :param str collection_version: version of collection.
        """
        view = self.navigate_to(
            self, 'Details', collection_name=collection_name, collection_version=collection_version
        )
        return view.read(widget_names=widget_names)


@navigator.register(AnsibleCollectionsEntity, 'All')
class ShowAllAnsibleCollections(NavigateStep):
    """navigate to Ansibel Collections Page"""

    VIEW = AnsibleCollectionsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Ansible Collections')


@navigator.register(AnsibleCollectionsEntity, 'Details')
class ShowAnsibleCollectionsDetails(NavigateStep):
    """Navigate to Ansible Collection Details page by clicking on
    collection name in the table
    Args:
        collection_name: The collection name.
        collection_version: The version of collection.
    """

    VIEW = AnsibleCollectionsDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('collection_name')
        stream_version = kwargs.get('collection_version')
        self.parent.search(f'name = {collection_name} and stream = {collection_version}')
        self.parent.table.row(name=collection_name, stream=collection_name)['Name'].widget.click()

    def post_navigate(self, _tries, *args, **kwargs):
        wait_for(
            lambda: self.am_i_here(*args, **kwargs),
            timeout=30,
            delay=1,
            handle_exception=True,
            logger=self.view.logger,
        )

    def am_i_here(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        return self.view.is_displayed
