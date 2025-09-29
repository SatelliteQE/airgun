from widgetastic.exceptions import NoSuchElementException

from airgun.exceptions import DisabledWidgetError
from airgun.helpers.base import BaseEntityHelper
from airgun.views.common import BookmarkCreateView


class BaseEntity:
    HELPER_CLASS = BaseEntityHelper

    def __init__(self, browser):
        self.browser = browser
        self.session = browser.extra_objects["session"]
        self.navigate_to = self.session.navigator.navigate
        self._helper = self.HELPER_CLASS(self)

    @property
    def helper(self):
        return self._helper

    def create_bookmark(self, values, search_query=None):
        """Create a bookmark.

        :param dict values: dictionary with keys 'name', 'query', 'public'
        :param str optional search_query: a query to type into searchbox if
            needed. Such query will be automatically populated as 'query' field
            for bookmark
        """
        # not using separate navigator step here not to have to register
        # navigate step for every single entity
        view = self.navigate_to(self, "All")
        if not hasattr(view, "searchbox"):
            raise KeyError(f"{self.__class__.__name__} does not have searchbox")
        if not view.searchbox.actions.is_displayed:
            raise NoSuchElementException(
                f"Unable to create a bookmark - {self.__class__.__name__} "
                "has a searchbox with no actions dropdown"
            )
        if search_query:
            view.searchbox.search_field.fill(search_query)
        view.searchbox.actions.fill("Bookmark this search")
        view = BookmarkCreateView(self.browser)
        view.fill(values)
        if not view.submit.is_enabled:
            message = view.error_message.text
            view.cancel.click()
            raise DisabledWidgetError(message)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search_menu(self, query: str) -> list[str]:
        """Perform a search of the vertical navigation menu.

        :param str query: search query for the vertical navigation menu
        :return list[str]: search results
        """
        view = self.navigate_to(self, "All")
        return view.menu_search.search(query)
