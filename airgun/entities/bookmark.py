from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.bookmark import BookmarkEditView
from airgun.views.bookmark import BookmarksView


def _gen_queries(entity_name, controller=None):
    """Generate search query and row filtering query from bookmark name and
    controller if passed.
    """
    row_query = {'name': entity_name}
    search_query = f'name = "{entity_name}"'
    if controller:
        search_query = f'{search_query} and controller = "{controller}"'
        row_query['controller'] = controller
    return search_query, row_query


class BookmarkEntity(BaseEntity):
    endpoint_path = '/bookmarks'

    # Note: creation procedure takes place on specific entity page, generic
    # helper is implemented inside :class:`BaseEntity`.

    def delete(self, entity_name, controller=None):
        """Delete existing bookmark"""
        view = self.navigate_to(self, 'All')
        query, row_query = _gen_queries(entity_name, controller)
        view.search(query)
        view.table.row(**row_query)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, query):
        """Search for bookmark"""
        view = self.navigate_to(self, 'All')
        return view.search(query)

    def read(self, entity_name, controller=None, widget_names=None):
        """Read bookmark values"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name, controller=controller)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values, controller=None):
        """Update existing bookmark"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name, controller=controller)
        result = view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
        return result


@navigator.register(BookmarkEntity, 'All')
class ShowAllBookmarks(NavigateStep):
    """Navigate to All Bookmarks screen."""

    VIEW = BookmarksView

    def step(self, *args, **kwargs):
        self.view.menu.select('Administer', 'Bookmarks')


@navigator.register(BookmarkEntity, 'Edit')
class EditBookmark(NavigateStep):
    """Navigate to Edit Bookmark screen.

    Args:
        entity_name: name of bookmark
        (optional) controller: name of controller for bookmark
    """

    VIEW = BookmarkEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        controller = kwargs.get('controller')
        query, row_query = _gen_queries(entity_name, controller)
        self.parent.search(query)
        self.parent.table.row(**row_query)['Name'].widget.click()
