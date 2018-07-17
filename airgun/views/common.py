from widgetastic.widget import (
    do_not_read_this_widget,
    ParametrizedLocator,
    ParametrizedView,
    Text,
    View,
    WTMixin,
)
from widgetastic_patternfly import Tab, TabWithDropdown

from airgun.widgets import (
    ACEEditor,
    ContextSelector,
    LCESelector,
    SatFlashMessages,
    SatSubscriptionsTable,
    SatTable,
    SatVerticalNavigation,
    Search,
    Select,
    ToggleRadioGroup,
    ValidationErrors,
)


class BaseLoggedInView(View):
    menu = SatVerticalNavigation('.//div[@id="vertical-nav"]/ul')
    taxonomies = ContextSelector()
    flash = SatFlashMessages(
        locator='//div[@class="toast-notifications-list-pf"]')
    validations = ValidationErrors()
    # TODO Defining current user procedure needs to be improved as it is not
    # simple field, but a dropdown menu that contains more items/actions
    current_user = Text("//a[@id='account_menu']")


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

    @property
    def is_displayed(self):
        return 'ng-hide' not in self.parent_browser.classes(self.TAB_LOCATOR)

    def read(self):
        """Do not attempt to read hidden tab contents"""
        if not self.is_displayed:
            do_not_read_this_widget()
        return super().read()


class SatVerticalTab(SatTab):
    """Represent vertical tabs that usually used in location and organization
    entities

    Usage::

        @View.nested
        class mytab(SatVerticalTab):
            TAB_NAME = 'My Tab'
    """
    TAB_LOCATOR = ParametrizedLocator(
        ".//ul[@data-tabs='pills']"
        "/li[./a[normalize-space(.)={@tab_name|quote}]]"
    )


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
        './/nav[@class="ng-scope" or not(@*)]/following-sibling::div')


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
    ROOT = (".//div[@path-selector='environments' or "
            "@path-selector='availableEnvironments']")

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
    table = SatTable(locator=".//table")

    @View.nested
    class ListRemoveTab(SatSecondaryTab):
        TAB_NAME = 'List/Remove'
        searchbox = Search()
        remove_button = Text(
            './/div[@data-block="list-actions"]'
            '//button[contains(@ng-click, "remove")]'
        )

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
            return self.parent_view.table.read()

    @View.nested
    class AddTab(SatSecondaryTab):
        TAB_NAME = 'Add'
        searchbox = Search()
        add_button = Text(
            './/div[@data-block="list-actions"]'
            '//button[contains(@ng-click, "add")]'
        )

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
            return self.parent_view.table.read()

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
    table = SatSubscriptionsTable(locator=".//table")


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


class SearchableViewMixin(WTMixin):
    """Mixin which adds :class:`airgun.widgets.Search` widget and
    :meth:`search` to your view. It's useful for _most_ entities list views
    where searchbox and results table are present.

    Note that class which uses this mixin should have :attr:`table` attribute.
    """
    searchbox = Search()
    welcome_message = Text("//div[@class='blank-slate-pf' or @id='welcome']")

    def is_searchable(self):
        """Verify that search procedure can be executed against specific page.
        That means that we have search field present on the page and that page
        is not a welcome one
        """
        if (not self.searchbox.search_field.is_displayed
                and self.welcome_message.is_displayed):
            return False
        return True

    def search(self, query):
        """Perform search using searchbox on the page and return table
        contents.

        :param str query: search query to type into search field. E.g. ``foo``
            or ``name = "bar"``.
        :return: list of dicts representing table rows
        :rtype: list
        """
        if not hasattr(self, 'table'):
            raise AttributeError(
                'Class {} does not have attribute "table". SearchableViewMixin'
                ' only works with views, which have table for results. Please '
                'define table or use custom search implementation instead'
                .format(self.__class__.__name__)
            )
        if not self.is_searchable():
            return None
        self.searchbox.search(query)

        return self.table.read()
