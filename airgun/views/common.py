import six
from widgetastic.widget import (
    NoSuchElementException,
    ParametrizedLocator,
    Table,
    Text,
    View,
    WidgetMetaclass,
)
from widgetastic_patternfly import Tab, TabWithDropdown

from airgun.widgets import ContextSelector, SatVerticalNavigation, Search


class BaseLoggedInView(View):
    menu = SatVerticalNavigation('.//div[@id="vertical-nav"]/ul')
    taxonomies = ContextSelector()


class SatTab(Tab):
    """Regular primary level ``Tab``.

    Usage::

        @View.nested
        class mytab(SatTab):
            TAB_NAME = 'My Tab'

    Note that ``TAB_NAME`` is optional and if it's absent - capitalized class
    name is used instead, which is useful for simple tab names like
    'Subscriptions'::

        @View.nested
        class subscriptions(SatTab):
            # no need to specify 'TAB_NAME', it will be set to 'Subscriptions'
            # automatically
            pass

    """
    ROOT = ParametrizedLocator(
        './/div[contains(@class, "page-content") or '
        'contains(@class, "tab-content")]')


class SatTabWithDropdown(TabWithDropdown):
    """Regular primary level ``Tab`` with dropdown.

    Usage::

        @View.nested
        class mytab(SatTabWithDropdown):
            TAB_NAME = 'My Tab'
            SUB_ITEM = 'My Tab Dropdown Item'
    """
    ROOT = ParametrizedLocator(
        './/div[contains(@class, "page-content") or '
        'contains(@class, "tab-content")]')


class SatSecondaryTab(Tab):
    """Secondary level Tab, typically 'List/Remove' or 'Add' sub-tab inside
    some primary tab.

    Usage::

        @View.nested
        class listremove(SatSecondaryTab):
            TAB_NAME = 'List/Remove'
    """
    ROOT = ParametrizedLocator(
        './/nav[@class="ng-scope"]/following-sibling::div')


class AddRemoveResourcesView(View):
    """View which allows assigning/unassigning some resources to entity.
    Contains two secondary level tabs 'List/Remove' and 'Add' with tables
    allowing managing resources for entity.

    Usage::

        @View.nested
        class resources(AddRemoveResourcesView): pass

    Note that locator for checkboxes of resources in tables can be overwritten
    for rare cases like Subscriptions where every entry consists of multiple
    table rows::

        @View.nested
        class resources(AddRemoveResourcesView):
            checkbox_locator = (
                './/table//tr[td[normalize-space(.)="%s"]]/'
                'following-sibling::tr//input[@type="checkbox"]')
    """
    checkbox_locator = (
        './/tr[td[normalize-space(.)="%s"]]/td[@class="row-select"]'
        '/input[@type="checkbox"]')

    @View.nested
    class ListRemoveTab(SatSecondaryTab):
        TAB_NAME = 'List/Remove'
        searchbox = Search()
        remove_button = Text(
            './/div[@data-block="list-actions"]'
            '//button[contains(@ng-click, "remove")]'
        )
        table = Table(locator=".//table")
        columns_exists = Text(
            ".//table//*[contains(name(), 'body')]/tr[1]/td[2]")

        def search(self, value):
            self.searchbox.search(value)
            return self.browser.element(
                self.parent_view.checkbox_locator % value)

        def remove(self, value):
            checkbox = self.search(value)
            checkbox.click()
            self.remove_button.click()

        def fill(self, values):
            if not isinstance(values, list):
                values = list((values,))
            for value in values:
                self.remove(value)

        def read(self):
            if self.columns_exists.is_displayed:
                return [row.name.text for row in self.table.rows()]
            return []

    @View.nested
    class AddTab(SatSecondaryTab):
        TAB_NAME = 'Add'
        searchbox = Search()
        add_button = Text(
            './/div[@data-block="list-actions"]'
            '//button[contains(@ng-click, "add")]'
        )
        table = Table(locator=".//table")
        columns_exists = Text(
            ".//table//*[contains(name(), 'body')]/tr[1]/td[2]")

        def search(self, value):
            self.searchbox.search(value)
            return self.browser.element(
                self.parent_view.checkbox_locator % value)

        def add(self, value):
            checkbox = self.search(value)
            checkbox.click()
            self.add_button.click()

        def fill(self, values):
            if not isinstance(values, list):
                values = list((values,))
            for value in values:
                self.add(value)

        def read(self):
            if self.columns_exists.is_displayed:
                return [row.name.text for row in self.table.rows()]
            return []

    def add(self, values):
        """Assign some resource(s).

        :param str or list values: string containing resource name or a list of
            such strings.
        """
        return self.AddTab.fill(values)

    def remove(self, values):
        """Unassign some resource(s).

        :param str or list values: string containing resource name or a list of
            such strings.
        """
        return self.ListRemoveTab.fill(values)

    def read(self):
        """Read all table values from both resource tables"""
        return {
            'assigned': self.ListRemoveTab.read(),
            'unassigned': self.AddTab.read(),
        }


class WidgetMixin(six.with_metaclass(WidgetMetaclass, object)):
    """Base class for all View and Widget mixins"""
    # todo: remove it and use widgetastic native one, once it's introduced
    pass


class SearchableViewMixin(WidgetMixin):
    """Mixin which adds :class:`airgun.widgets.Search` widget and
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
