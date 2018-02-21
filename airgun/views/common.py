from selenium.common.exceptions import NoSuchElementException
from widgetastic.widget import View

from airgun.widgets import HorizontalNavigation, ContextSelector, Search


class BaseLoggedInView(View):
    menu = HorizontalNavigation()
    taxonomies = ContextSelector()


class SearchableView(View):
    """"Mixin" view which adds :class:`airgun.widgets.Search` widget and
    :meth:`search` to your view. It's useful for _most_ entities list views
    where searchbox is present.

    Note that you can override expected result locator for the element which is
    returned by :meth:`search` by specifying custom ``search_result_locator``
    string variable in your view class.
    """
    searchbox = Search()
    search_result_locator = "//a[contains(., '%s')]"

    def search(self, query, expected_result=None):
        """Perform search using searchbox on the page and return element text
        if found.

        :param str query: search query to type into search field. E.g. ``foo``
            or ``name = "bar"``.
        :param str optional expected_result: expected resulting entity name.
            Useful when you specify custom search query, not just entity name.
            Defaults to ``query``.
        :return: name of entity (if found) or None
        :rtype: str or None
        """
        self.searchbox.search(query)
        try:
            result = self.browser.element(
            self.search_result_locator % (expected_result or query)).text
        except NoSuchElementException:
            result = None
        return result
