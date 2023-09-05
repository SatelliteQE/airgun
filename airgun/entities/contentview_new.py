from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.contentview_new import NewContentViewCreateView
from airgun.views.contentview_new import NewContentViewTableView
from airgun.views.contentview_new import NewContentViewEditView
from airgun.views.contentview_new import NewContentViewVersionPublishView
from airgun.views.contentview_new import CreateFilterView 


class NewContentViewEntity(BaseEntity):
    endpoint_path = '/content_views'

    def create(self, values):
        """Create a new content view"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()

    def search(self, value):
        """Search for content view"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def publish(self, entity_name, values=None):
        """Publishes to create new version of CV and promotes the contents to
        'Library' environment.
        :return: dict with new content view version table row; contains keys
            like 'Version', 'Status', 'Environments' etc.
        """
        view = self.navigate_to(self, 'Publish', entity_name=entity_name)
        if values:
            view.fill(values)
        view.next.click()
        view.finish.click()
        view.progressbar.wait_for_result()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.versions.table.read()

    def create_filter(self, entity_name, filter_name, filter_type, filter_inclusion):
        """Create a new filter on a CV - filter_type should be one of the available dropdown options
        in the Content Type dropdown, and filter_inclusion should be either 'include' or 'exclude'
        :return: dict with new filter table row
        """
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.new_filter.click()
        view = CreateFilterView(self.browser)
        view.name.fill(filter_name)
        view.filterType.fill(filter_type)
        if filter_inclusion == 'include':
            view.includeFilter.fill(True)
        elif filter_inclusion == 'exclude':
            view.excludeFilter.fill(True)
        else:
            raise ValueError("Filter_inclusion must be one of include or exclude.")
        view.create.click()
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.filters.table.read()

    def delete_filter(self, entity_name, filter_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.filters.search(filter_name)
        view.filters.table[0][6].widget.item_select('Remove')
        #Attempt to read the table, and if there isn't one return True, else delete failed so return False
        try:
            view.filters.table.read()
        except:
            return True
        else:
            return False



@navigator.register(NewContentViewEntity, 'All')
class ShowAllContentViewsScreen(NavigateStep):
    """Navigate to All Content Views screen."""

    VIEW = NewContentViewTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Content', 'Lifecycle', 'Content Views')


@navigator.register(NewContentViewEntity, 'New')
class CreateContentView(NavigateStep):
    """Navigate to Create content view."""

    VIEW = NewContentViewCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_content_view.click()


@navigator.register(NewContentViewEntity, 'Edit')
class EditContentView(NavigateStep):
    """Navigate to Edit Content View screen.
    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewContentViewEntity, 'Publish')
class PublishContentViewVersion(NavigateStep):
    """Navigate to Content View Publish screen.
    Args:
        entity_name: name of content view
    """

    VIEW = NewContentViewVersionPublishView

    def prerequisite(self, *args, **kwargs):
        """Open Content View first."""
        return self.navigate_to(self.obj, 'Edit', entity_name=kwargs.get('entity_name'))

    def step(self, *args, **kwargs):
        """Click 'Publish new version' button"""
        self.parent.publish.click()

