from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
    ParametrizedLocator,
    ParametrizedView,
    Text,
    TextInput,
    View,
    WTMixin,
    do_not_read_this_widget,
)
from widgetastic_patternfly import BreadCrumb, Tab, TabWithDropdown
from widgetastic_patternfly4 import Button, Select
from widgetastic_patternfly4.navigation import Navigation
from widgetastic_patternfly4.ouia import Dropdown, PatternflyTable

from airgun.utils import get_widget_by_name, normalize_dict_values
from airgun.widgets import (
    ACEEditor,
    ContextSelector,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    ItemsList,
    LCESelector,
    Pf4ConfirmationDialog,
    PF4LCECheckSelector,
    PF4LCESelector,
    PF4NavSearch,
    PF4Search,
    ProgressBar,
    ReadOnlyEntry,
    SatFlashMessages,
    SatSubscriptionsTable,
    SatTable,
    Search,
    ValidationErrors,
)


class BaseLoggedInView(View):
    """Base view for Satellite pages"""

    menu = Navigation("Global")
    menu_search = PF4NavSearch()
    taxonomies = ContextSelector()
    flash = SatFlashMessages()
    validations = ValidationErrors()
    dialog = Pf4ConfirmationDialog()
    logout = Text("//a[@href='/users/logout']")
    current_user = Dropdown('user-info-dropdown')
    account_menu = Dropdown('user-info-dropdown')
    permission_denied = Text('//*[@id="content"]')

    def select_logout(self):
        """logout from satellite"""
        self.account_menu.click()
        self.logout.click()

    def read(self, widget_names=None, limit=None):
        """Reads the contents of the view and presents them as a dictionary.

        :param widget_names: If specified, will read only the widgets names in the list.
        :param limit: how many entries to fetch at most

        :return: A :py:class:`dict` of ``widget_name: widget_read_value``
            where the values are retrieved using the :py:meth:`Widget.read`.
        """
        if widget_names is None:
            if limit is not None:
                raise NotImplementedError("You must specify widgets to be able to specify limit")
            return super().read()
        if not isinstance(widget_names, list | tuple):
            widget_names = [widget_names]
        values = {}
        for widget_name in widget_names:
            widget = get_widget_by_name(self, widget_name)
            if hasattr(widget, 'read_limited') and callable(widget.read_limited):
                values[widget_name] = widget.read(limit=limit)
            else:
                values[widget_name] = widget.read()
        return normalize_dict_values(values)


class WrongContextAlert(View):
    """Alert screen which appears when switching organization while organization-specific entity is
    opened.
    """

    message = Text(
        "//div[contains(@class, 'alert-warning')]"
        "[span[normalize-space(.)='Please try to update your request']]"
    )
    back = Button(href='/')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.message, exception=False) is not None


class SatTab(Tab):
    """Regular primary level ``Tab``.

    Usage::

        @View.nested
        class mytab(SatTab):
            TAB_NAME = 'My Tab'
        @View.nested
        class subscriptions(SatTab):
            # no need to specify 'TAB_NAME', it will be set to 'Subscriptions'
            # automatically
            pass

    Note that ``TAB_NAME`` is optional and if it's absent - capitalized class
    name is used instead, which is useful for simple tab names like
    'Subscriptions'
    """

    ROOT = ParametrizedLocator(
        './/div[contains(@class, "page-content") or contains(@class, "tab-content")]'
    )

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
        ".//ul[@data-tabs='pills']/li[./a[normalize-space(.)={@tab_name|quote}]]"
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
        './/div[contains(@class, "page-content") or contains(@class, "tab-content")]'
    )

    @property
    def is_displayed(self):
        return 'ng-hide' not in self.parent_browser.classes(self.TAB_LOCATOR)

    def read(self):
        """Do not attempt to read hidden tab contents"""
        if not self.is_displayed:
            do_not_read_this_widget()
        return super().read()


class SatSecondaryTab(SatTab):
    """Secondary level Tab, typically 'List/Remove' or 'Add' sub-tab inside
    some primary tab.

    Usage::

        @View.nested
        class listremove(SatSecondaryTab):
            TAB_NAME = 'List/Remove'
    """

    ROOT = ParametrizedLocator('.//nav[@class="ng-scope" or not(@*)]/following-sibling::div')

    TAB_LOCATOR = ParametrizedLocator(
        './/nav[@class="ng-scope" or not(@*)]/ul[contains(@class, "nav-tabs")]'
        '/li[./a[normalize-space(.)={@tab_name|quote}]]'
    )


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

    ROOT = (
        ".//*[self::div or self::span][@path-selector='environments' or "
        "@path-selector='availableEnvironments']"
    )

    PARAMETERS = ('lce_name',)

    LAST_ENV = ".//div[contains(@class, 'path-selector')]/ul/li[last()]"
    lce = LCESelector(
        locator=ParametrizedLocator(
            "./div[contains(@class, 'path-selector')]/ul[li[normalize-space(.)='{lce_name}']]"
        )
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

        Usage::

            my_view.lce.fill({'PROD': True})
            my_view.lce.fill({'PROD': 'Library'})

        Value ``True`` or ``False`` means to set corresponding checkbox value
        to the last checkbox available in widget (last lifecycle environment).
        If you want to select different lifecycle environment within the same
        route - pass its name as a value instead
        """
        if values in (True, False):
            values = {self.context['lce_name']: values}
        else:
            values = {values: True}
        return self.lce.fill(values)

    def read(self):
        """Shortcut which returns value of included ``lce``

        :class:`airgun.widgets.LCESelector` widget.

        Note that returned result will be wrapped in extra dict due to
        :class:`widgetastic.widget.ParametrizedView` nature::

            {
                'DEV': {'Library': False, 'DEV': True},
                'QA': {'Library': False, 'IT': True},
                'PROD': {'Library': False, 'PROD': True},
            }

        """
        return self.lce.read()


class PF4LCESelectorGroup(LCESelectorGroup):
    ROOT = './/div[./div[@class="env-path"]]'

    PARAMETERS = ('lce_name',)

    LAST_ENV = './/div[@class="env-path"][last()]'
    lce = PF4LCESelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


class PF4LCECheckSelectorGroup(PF4LCESelectorGroup):
    """Checkbox version of PF4 LCE Selector"""

    lce = PF4LCECheckSelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


class PF4LCEGroup(ParametrizedLocator):
    "Group of LCE indicators"
    ROOT = './/td and '

    PARAMETERS = ('lce_name',)

    LAST_ENV = './/div[@class="env-path"][last()]'
    lce = PF4LCESelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


class ListRemoveTab(SatSecondaryTab):
    """'List/Remove' tab, part of :class:`AddRemoveResourcesView`."""

    TAB_NAME = 'List/Remove'
    searchbox = Search()
    remove_button = Text(
        './/div[@data-block="list-actions"]//button[contains(@ng-click, "remove")]'
    )
    table = SatTable(
        locator=".//table", column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
    )

    def search(self, value):
        """Search for specific associated resource and return the results"""
        self.searchbox.search(value)
        return self.table.read()

    def remove(self, value):
        """Remove specific associated resource"""
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.remove_button.click()

    def fill(self, values):
        """Remove associated resource(s)."""
        if not isinstance(values, list):
            values = [values]
        for value in values:
            self.remove(value)

    def read(self):
        """Return a list of associated resources"""
        return self.table.read()


class AddTab(SatSecondaryTab):
    TAB_NAME = 'Add'
    searchbox = Search()
    add_button = Text('.//div[@data-block="list-actions"]//button[contains(@ng-click, "add")]')
    table = SatTable(
        locator=".//table", column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
    )

    def search(self, value):
        """Search for specific available resource and return the results"""
        self.searchbox.search(value)
        return self.table.read()

    def add(self, value):
        """Associate specific resource"""
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.add_button.click()

    def fill(self, values):
        """Associate resource(s)"""
        if not isinstance(values, list):
            values = [values]
        for value in values:
            self.add(value)

    def read(self):
        """Return a list of available resources"""
        return self.table.read()


class AddRemoveResourcesView(View):
    """View which allows assigning/unassigning some resources to entity.
    Contains two secondary level tabs 'List/Remove' and 'Add' with tables
    allowing managing resources for entity.

    Usage::

        @View.nested
        class resources(AddRemoveResourcesView): pass

    """

    list_remove_tab = View.nested(ListRemoveTab)
    add_tab = View.nested(AddTab)

    def add(self, values):
        """Assign some resource(s).

        :param str or list values: string containing resource name or a list of
            such strings.
        """
        return self.add_tab.fill(values)

    def remove(self, values):
        """Unassign some resource(s).

        :param str or list values: string containing resource name or a list of
            such strings.
        """
        return self.list_remove_tab.fill(values)

    def read(self):
        """Read all table values from both resource tables"""
        return {
            'assigned': self.list_remove_tab.read(),
            'unassigned': self.add_tab.read(),
        }


class NewAddRemoveResourcesView(View):
    searchbox = PF4Search()
    status = Select(locator='.//div[@data-ouia-component-id="select Status"]')
    remove_button = Dropdown(locator='.//div[@data-ouia-component-id="repositoies-bulk-actions"]')
    add_button = Button(locator='.//button[@data-ouia-component-id="add-repositories"]')
    table = PatternflyTable(
        component_id='content-view-repositories-table',
        column_widgets={
            0: Checkbox(locator='.//input[@type="checkbox"]'),
            'Type': Text('.//a'),
            'Name': Text('.//a'),
            'Product': Text('.//a'),
            'Sync State': Text('.//a'),
            'Content': Text('.//a'),
            'Status': Text('.//a'),
        },
    )

    def select_status(self, value):
        """Set status box to passed in value"""
        self.status.fill(value)

    def search(self, value):
        """Search for specific available resource and return the results"""
        self.searchbox.search(value)
        return self.read()

    def add(self, value):
        """Associate specific resource"""
        self.select_status("Not added")
        self.search(value)
        value = self.table.rows()
        next(self.table.rows())[0].widget.fill(True)
        self.add_button.click()

    def fill(self, values):
        """Associate resource(s)"""
        for value in values:
            self.add(value)

    def remove(self, value):
        """Unassign some resource(s).
        :param str or list values: string containing resource name or a list of such strings.
        """
        self.select_status("Added")
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.remove_button.item_select('Remove')

    def read(self):
        """Read all table values from both resource tables"""
        self.browser.wait_for_element(locator='//h4[text()="Loading"]', exception=False)
        self.browser.wait_for_element(
            self.table, exception=False, ensure_page_safe=True, timeout=10
        )
        self.browser.plugin.ensure_page_safe(timeout='60s')
        self.table.wait_displayed()
        self.select_status("All")
        return self.table.read()


class AddRemoveSubscriptionsView(AddRemoveResourcesView):
    """A variant of :class:`AddRemoveResourcesView` for managing subscriptions.
    Subscriptions table has different structure - entity label is located in
    separate row apart from checkbox and other cells.
    """

    @View.nested
    class list_remove_tab(ListRemoveTab):
        table = SatSubscriptionsTable(
            locator=".//table", column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
        )

    @View.nested
    class add_tab(AddTab):
        table = SatSubscriptionsTable(
            locator=".//table", column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
        )


class TemplateEditor(View):
    """Default view for template entity editor that can be present for example
    on provisioning template of partition table pages. It contains from
    different options of content rendering and ace editor where you can
    actually provide your inputs

    Usage::

        editor = View.nested(TemplateEditor)

    """

    ROOT = ".//div[@id='editor-container']"
    rendering_options = ItemsList(".//div[contains(@class,'navbar-editor')]/ul")
    import_template = Button(id='import-btn')
    fullscreen = Button(id='fullscreen-btn')
    editor = ACEEditor()


class SearchableViewMixin(WTMixin):
    """Mixin which adds :class:`airgun.widgets.Search` widget and
    :meth:`airgun.widgets.Search.search` to your view. It's useful for _most_ entities list views
    where searchbox and results table are present.

    Note that class which uses this mixin should have :attr: `table` attribute.
    """

    searchbox = Search()
    welcome_message = Text("//div[@class='blank-slate-pf' or @id='welcome']")

    def is_searchable(self):
        """Verify that search procedure can be executed against specific page.
        That means that we have search field present on the page and that page
        is not a welcome one
        """
        if self.searchbox.search_field.is_displayed and (not self.welcome_message.is_displayed):
            return True
        return False

    def search(self, query):
        """Perform search using searchbox on the page and return table
        contents.

        :param str query: search query to type into search field. E.g. ``foo``
            or ``name = "bar"``.
        :return: list of dicts representing table rows
        :rtype: list
        """
        if not hasattr(self.__class__, 'table'):
            raise AttributeError(
                f'Class {self.__class__.__name__} does not have attribute "table". '
                'SearchableViewMixin only works with views, which have table for results. '
                'Please define table or use custom search implementation instead'
            )
        if not self.is_searchable():
            return None
        self.searchbox.search(query)
        if hasattr(self, 'title'):
            self.title.click()
        return self.table.read()


class SearchableViewMixinPF4(SearchableViewMixin):
    """Mixin which adds :class:`airgun.widgets.Search` widget and
    :meth:`airgun.widgets.Search.search` to your view. It's useful for _most_ entities list views

    where searchbox and results table are present.
    Note that class which uses this mixin should have :attr: `table` attribute.
    """

    searchbox = PF4Search()
    blank_page = Text("//div[contains(@class, 'pf-c-empty-state')]")

    def is_searchable(self):
        """Verify that search procedure can be executed against specific page
        that is not blank
        """
        if self.searchbox.search_field.is_displayed and (not self.blank_page.is_displayed):
            return True
        return False

    def search(self, query):
        """Perform search using searchbox on the page and return table
        contents.

        :param str query: search query to type into search field. E.g. ``foo``
            or ``name = "bar"``.
        :return: list of dicts representing table rows
        :rtype: list
        """
        if not hasattr(self.__class__, 'table'):
            raise AttributeError(
                f'Class {self.__class__.__name__} does not have attribute "table". '
                'SearchableViewMixin only works with views, which have table for results. '
                'Please define table or use custom search implementation instead'
            )
        if not self.is_searchable():
            return None
        self.searchbox.search(query)
        self.browser.plugin.ensure_page_safe(timeout='60s')
        self.table.wait_displayed()
        if hasattr(self, 'title'):
            self.title.click()
        return self.table.read()


class TaskDetailsView(BaseLoggedInView):
    """Common view for task details screen. Can be found for most of tasks for
    various entities like Products, Repositories, Errata etc.
    """

    breadcrumb = BreadCrumb()
    action_type = ReadOnlyEntry(name='Action Type')
    user = ReadOnlyEntry(name='User')
    started_at = ReadOnlyEntry(name='Started At')
    finished_at = ReadOnlyEntry(name='Finished At')
    parameters = ReadOnlyEntry(name='Parameters')
    state = ReadOnlyEntry(name='State')
    result = ReadOnlyEntry(name='Result')
    progressbar = ProgressBar()
    details = ReadOnlyEntry(name='Details')


class BookmarkCreateView(BaseLoggedInView):
    """Bookmark creation modal window, available via searchbox dropdown ->
    Bookmark this search.

    Has slightly different style for katello and foreman pages, thus some
    widgets have special locators.
    """

    ROOT = ".//div[contains(@class, 'modal-dialog')]"

    title = Text(
        "//*[self::div[@data-block='modal-header'] or self::h4]"
        "[normalize-space(.) = 'Add Bookmark'"
        " or normalize-space(.) = 'Create Bookmark']"
    )
    name = TextInput(name='name')
    query = TextInput(name='query')
    error_message = Text(".//span[@class='error-message']")
    public = Checkbox(locator="//input[@type='checkbox'][@name='public' or @name='publik']")
    # text can be either 'Submit' or 'Save'
    submit = Text(".//button[@type='submit' or @ng-click='ok()']")
    # may contain <span> inside, using normalize-space
    cancel = Text(".//button[normalize-space(.)='Cancel']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class TemplateInputItem(GenericRemovableWidgetItem):
    """Template Input item view"""

    remove_button = Text(".//a[contains(@class, 'remove_nested_fields')]")
    name = TextInput(locator=".//input[contains(@name, '[name]')]")
    required = Checkbox(locator=".//input[contains(@id, 'required')]")
    input_type = FilteredDropdown(locator=".//div[contains(@id, 'input_type')]")

    input_content = ConditionalSwitchableView(reference='input_type')

    @input_content.register('User input')
    class UserInputForm(View):
        advanced = Checkbox(locator=".//input[contains(@id, 'advanced')]")
        options = TextInput(locator=".//textarea[contains(@name, '[options]')]")
        description = TextInput(locator=".//textarea[contains(@name, '[description]')]")

    @input_content.register('Fact value')
    class FactValueForm(View):
        fact_name = TextInput(locator=".//input[contains(@name, '[fact_name]')]")
        description = TextInput(locator=".//textarea[contains(@name, '[description]')]")

    @input_content.register('Variable')
    class VariableValueForm(View):
        variable_name = TextInput(locator=".//input[contains(@name, '[variable_name]')]")
        description = TextInput(locator=".//textarea[contains(@name, '[description]')]")

    @input_content.register('Puppet parameter')
    class PuppetParameterForm(View):
        puppet_class_name = TextInput(locator=".//input[contains(@name, '[puppet_class_name]')]")
        puppet_parameter_name = TextInput(
            locator=".//input[contains(@name, '[puppet_parameter_name]')]"
        )
        description = TextInput(locator=".//textarea[contains(@name, '[description]')]")


class WizardStepView(View):
    def __init__(self, parent, logger=None):
        """Expand the selected wizard step"""
        View.__init__(self, parent, logger=logger)
        self.expander.click()
