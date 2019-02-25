from widgetastic.exceptions import NoSuchElementException

from airgun.helpers.base import BaseEntityHelper
from airgun.views.common import BookmarkCreateView


class BaseEntity(object):

    entity_helper_class = BaseEntityHelper

    def __init__(self, browser):
        self.browser = browser
        self.session = browser.extra_objects['session']
        self.navigate_to = self.session.navigator.navigate
        self._helper = self.entity_helper_class(self)

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
        view = self.navigate_to(self, 'All')
        if not hasattr(view, 'searchbox'):
            raise KeyError(
                '{} does not have searchbox'.format(self.__class__.__name__))
        if not view.searchbox.actions.is_displayed:
            raise NoSuchElementException(
                'Unable to create a bookmark - {} has a searchbox with no'
                'actions dropdown'
                .format(self.__class__.__name__)
            )
        if search_query:
            view.searchbox.search_field.fill(search_query)
        view.searchbox.actions.fill('Bookmark this search')
        view = BookmarkCreateView(self.browser)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
