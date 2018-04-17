import six
from widgetastic.widget import (
    NoSuchElementException,
    ParametrizedLocator,
    ParametrizedView,
    Table,
    Text,
    View,
    WidgetMetaclass,
)
from widgetastic_patternfly import Tab, TabWithDropdown

from airgun.widgets import (
    ACEEditor,
    ContextSelector,
    LCESelector,
    SatFlashMessages,
    SatVerticalNavigation,
    Search,
    Select,
    ToggleRadioGroup,
)


class BaseLoggedInView(View):
    menu = SatVerticalNavigation('.//div[@id="vertical-nav"]/ul')
    taxonomies = ContextSelector()
    flash = SatFlashMessages(
        locator='//div[@class="toast-notifications-list-pf"]')


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


class LCESelectorGroup(ParametrizedView):
    """Group of :class:`airgun.widgets.LCESelector`, typically present on page
    for selecting desired lifecycle environment.

    Usage::

        lce = View.nested(LCESelectorGroup)

        #or

        @View.nested
        class lce(LCESelectorGroup):
            pass
    """
    ROOT = ".//div[@path-selector='environments']"

    PARAMETERS = ('lce_name',)

    LAST_ENV = ".//div[contains(@class, 'path-selector')]/ul/li[last()]"
    lce = LCESelector(
        locator=ParametrizedLocator(
            "./div[contains(@class, 'path-selector')]/ul"
            "[li[normalize-space(.)='{lce_name}']]")
    )

    @classmethod
    def all(cls, browser):
        """Helper method which returns list of tuples with all LCESelector
        names (last available environment is used as a name). It's required for
        :meth:`read` to work properly.
        """
        return [(element.text,) for element in browser.elements(cls.LAST_ENV)]

    def fill(self, values=None):
        """Shortcut to pass the value to included ``lce``
        :class:`airgun.widgets.LCESelector` widget. Usage remains the same as
        :class:`airgun.widgets.LCESelector` and
        :class:`widgetastic.widget.ParametrizedView` required param is filled
        automatically from passed lifecycle environment's name.

        Example::

            my_view.lce.fill({'PROD': True})

        Value ``True`` or ``False`` means to set corresponding checkbox value
        to the last checkbox available in widget (last lifecycle environment).
        If you want to select different lifecycle environment within the same
        route - pass its name as a value instead::

            my_view.lce.fill({'PROD': 'Library'})

        """
        if values in (True, False):
            values = {self.context['lce_name']: values}
        else:
            values = {values: True}
        return self.lce.fill(values)

    def read(self):
        """Shortcut which returns value of included ``lce``
        :class:`LCESelector` widget.

        Note that returned result will be wrapped in extra dict due to
        :class:`widgetastic.widget.ParametrizedView` nature::

            {
                'DEV': {'Library': False, 'DEV': True},
                'QA': {'Library': False, 'IT': True},
                'PROD': {'Library': False, 'PROD': True},
            }

        """
        return self.lce.read()


class AddRemoveResourcesView(View):
    """View which allows assigning/unassigning some resources to entity.
    Contains two secondary level tabs 'List/Remove' and 'Add' with tables
    allowing managing resources for entity.

    Usage::

        @View.nested
        class resources(AddRemoveResourcesView): pass

    Note that locator for checkboxes of resources in tables and labels getter
    method can be overwritten if needed.
    """
    checkbox_locator = (
        './/tr[td[normalize-space(.)="%s"]]/td[@class="row-select"]'
        '/input[@type="checkbox"]')

    @classmethod
    def table_labels(cls, table):
        """Returns a list of labels (entity names) in tables. Can be
        overwritten for tables with different column names or labels placement.
        """
        return [row.name.text for row in table.rows()]

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
                return self.parent_view.table_labels(self.table)
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
                return self.parent_view.table_labels(self.table)
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


class AddRemoveSubscriptionsView(AddRemoveResourcesView):
    """A variant of :class:`AddRemoveResourcesView` for managing subscriptions.
    Subscriptions table has different structure - entity label is located in
    separate row apart from checkbox and other cells.
    """
    checkbox_locator = (
        './/table//tr[td[normalize-space(.)="%s"]]'
        '/following-sibling::tr//input[@type="checkbox"]')

    @classmethod
    def table_labels(cls, table):
        return [
            row.quantity.text for row
            in table.rows(
                _row__attr_contains=('class', 'row-selector-label'))
        ]


class TemplateEditor(View):
    """Default view for template entity editor that can be present for example
    on provisioning template of partition table pages. It contains from
    different options of content rendering and ace editor where you can
    actually provide your inputs

    Usage::

        editor = View.nested(TemplateEditor)

    """
    ROOT = ".//div[@class='editor-container']"
    rendering_options = ToggleRadioGroup(".//div[@class='btn-group']")
    import_template = Text(".//a[normalize-space(.)='Import']")
    fullscreen = Text(".//a[normalize-space(.)='Fullscreen']")
    syntax_type = Select(id='mode')
    key_binding = Select(id='keybinding')
    editor = ACEEditor()


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
