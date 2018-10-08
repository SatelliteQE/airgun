from widgetastic.exceptions import NoSuchElementException

from airgun.views.common import BookmarkCreateView


class BaseEntity(object):

    def __init__(self, browser):
        self.browser = browser
        self.session = browser.extra_objects['session']
        self.navigate_to = self.session.navigator.navigate

    def create_bookmark(self, values, search_query=None):
        """Create a bookmark.

        :param dict values: dictionary with keys 'name', 'query', 'public'
        :param str optional search_query: if something different from `query`
            should be typed into searchbox
        """
        # not using separate navigator step here not to have to register
        # navigate step for every single entity
        view = self.navigate_to(self, 'All')
        if not search_query:
            search_query = values.get('query')
        if not hasattr(view, 'search'):
            raise KeyError(
                '{} does not have searchbox'.format(self.__class__.__name__))
        view.search(search_query)
        if not view.searchbox.actions.is_displayed:
            raise NoSuchElementException(
                'Unable to create a bookmark - {} has a searchbox with no'
                'actions dropdown'
                .format(self.__class__.__name__)
            )
        view.searchbox.actions.fill('Bookmark this search')
        view = BookmarkCreateView(self.browser)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()
