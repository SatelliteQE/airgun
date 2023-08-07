from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.modulestream import ModuleStreamsDetailsView
from airgun.views.modulestream import ModuleStreamView


class ModuleStreamEntity(BaseEntity):
    endpoint_path = '/module_streams'

    def search(self, query):
        """Search for module stream

        :param str query: search query to type into search field. E.g.
            ``name = "ant"``.
        """
        view = self.navigate_to(self, 'All')
        return view.search(query)

    def read(self, entity_name, stream_version, widget_names=None):
        """Read module streams values from Module Stream Details page

        :param str entity_name: the module stream name to read.
        :param str stream_version: stream version of module.
        """
        view = self.navigate_to(
            self, 'Details', entity_name=entity_name, stream_version=stream_version
        )
        return view.read(widget_names=widget_names)


@navigator.register(ModuleStreamEntity, 'All')
class ShowAllModuleStreams(NavigateStep):
    """navigate to Module Streams Page"""

    VIEW = ModuleStreamView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Content Types', 'Module Streams')


@navigator.register(ModuleStreamEntity, 'Details')
class ShowModuleStreamsDetails(NavigateStep):
    """Navigate to Module Stream Details page by clicking on
    necessary module name in the table

    Args:
        entity_name: The module name.
        module_version: The version of module stream.
    """

    VIEW = ModuleStreamsDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        stream_version = kwargs.get('stream_version')
        self.parent.search(f'name = {entity_name} and stream = {stream_version}')
        self.parent.table.row(name=entity_name, stream=stream_version)['Name'].widget.click()

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
        return self.view.is_displayed and self.view.breadcrumb.locations[1].startswith(entity_name)
