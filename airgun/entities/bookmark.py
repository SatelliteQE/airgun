from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.bookmark import BookmarkEditView, BookmarksView


class BookmarkEntity(BaseEntity):

    # Note: creation procedure takes place on specific entity page, generic
    # helper is implemented inside :class:`BaseEntity`.

    def delete(self, entity_name, controller=None):
        """Delete existing bookmark"""
        view = self.navigate_to(self, 'All')
        row_query = {'name': entity_name}
        if not controller:
            query = entity_name
        else:
            query = 'name = "{}" and controller = "{}"'.format(
                entity_name, controller)
            row_query['controller'] = controller
        view.search(query)
        view.table.row(**row_query)['Actions'].widget.click(handle_alert=True)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, query):
        """Search for bookmark"""
        view = self.navigate_to(self, 'All')
        return view.search(query)

    def read(self, entity_name, controller=None):
        """Read bookmark values"""
        view = self.navigate_to(
            self, 'Edit', entity_name=entity_name, controller=controller)
        return view.read()

    def update(self, entity_name, values, controller=None):
        """Update existing bookmark"""
        view = self.navigate_to(
            self, 'Edit', entity_name=entity_name, controller=controller)
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
        row_query = {'name': entity_name}
        if not controller:
            query = entity_name
        else:
            query = 'name = "{}" and controller = "{}"'.format(
                entity_name, controller)
            row_query['controller'] = controller
        self.parent.search(query)
        self.parent.table.row(**row_query)['Name'].widget.click()
