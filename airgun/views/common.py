from contextlib import contextmanager
import time

from selenium.common.exceptions import ElementNotInteractableException
from wait_for import wait_for
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
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4.navigation import Navigation
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Dropdown,
)
from widgetastic_patternfly5.ouia import (
    Dropdown as PF5OUIADropdown,
    PatternflyTable,
    Select as PF5OUIASelect,
)

from airgun.utils import get_widget_by_name, normalize_dict_values
from airgun.widgets import (
    ACEEditor,
    ContextSelector,
    FilteredDropdown,
    GenericRemovableWidgetItem,
    ItemsList,
    LCESelector,
    Pf4ConfirmationDialog,
    PF5LCECheckSelector,
    PF5LCESelector,
    PF5NavSearch,
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

    menu = Navigation('Global')
    menu_search = PF5NavSearch()
    taxonomies = ContextSelector()
    flash = SatFlashMessages()
    validations = ValidationErrors()
    dialog = Pf4ConfirmationDialog()
    logout = Text("//a[@href='/users/logout']")
    current_user = PF5OUIADropdown('user-info-dropdown')
    account_menu = PF5OUIADropdown('user-info-dropdown')
    permission_denied = Text(
        '//*[@id="content" or contains(@class, "pf-v5-c-empty-state pf-m-xl")]'
    )
    product = Text('//span[@class="navbar-brand-txt"]/span')

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
                raise NotImplementedError('You must specify widgets to be able to specify limit')
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

    def documentation_links(self):
        """Return Documentation links present on the given page if any.
        Note: This is not a full-proof helper. For example, it can't get links hidden behind a dropdown button.
        """
        doc_link_elements = (
            '//a[contains(text(), "documentation") or contains(text(), "Documentation") or '
            'contains(@class, "btn-docs") or contains(@href, "console.redhat.com") or '
            'contains(@href, "access.redhat.com") or contains(@href, "docs.redhat.com") or '
            'contains(@href, "www.redhat.com") or contains(@href, "links") or '
            'contains(text(), "Try the Satellite upgrade helper") or '
            'contains(text(), "Contact support")]'
        )
        doc_links = []
        for item in self.browser.elements(doc_link_elements):
            try:
                item.click()
                if len(self.browser.window_handles) == 1:
                    doc_links.extend([self.browser.url])
                    self.browser.selenium.back()
                else:
                    self.browser.switch_to_window(self.browser.window_handles[1])
                    doc_links.extend([self.browser.url])
                    self.browser.switch_to_window(self.browser.window_handles[0])
                    self.browser.close_window(self.browser.window_handles[1])
            except ElementNotInteractableException:
                # Adding this because some links are hidden behind dropdown button.
                # To Do: Handle doc buttons hidden behind drop down buttons.
                doc_links.extend([item.get_attribute('href')])
                continue
        return doc_links


class PF5ModalViewMixin(WTMixin):
    """Mixin for PatternFly 5 Modals"""

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.ROOT, visible=True, timeout=10, exception=False)
            is not None
        )

    def wait_animation_end(self):
        self.browser.wait_for_element(self.ROOT, visible=True, timeout=20)


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
        return self.message.is_displayed


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


class PF5LCESelectorGroup(LCESelectorGroup):
    ROOT = './/div[./div[@class="env-path"]]'

    PARAMETERS = ('lce_name',)

    LAST_ENV = './/div[@class="env-path"][last()]'
    lce = PF5LCESelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


class PF5LCECheckSelectorGroup(PF5LCESelectorGroup):
    """Checkbox version of PF5 LCE Selector"""

    lce = PF5LCECheckSelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


# PF5 kebab menu present in table rows
class TableRowKebabMenu(Dropdown):
    """Dropdown for PF5 kebab menus used in table rows."""

    ROOT = '.'
    DEFAULT_LOCATOR = './/button[contains(@class, "-c-menu-toggle") and @aria-label="Kebab toggle"]'


class PF5LCEGroup(ParametrizedLocator):
    "Group of LCE indicators"

    ROOT = './/td and '

    PARAMETERS = ('lce_name',)

    LAST_ENV = './/div[@class="env-path"][last()]'
    lce = PF5LCESelector(
        locator=ParametrizedLocator(
            './/div[@class="env-path" and .//*[contains(normalize-space(.), "{lce_name}")]]'
        )
    )


class SearchableViewMixin(WTMixin):
    """Enhanced searchable table mixin with debounce delay for PatternFly UIs.

    Adds explicit SEARCH_DELAY to handle delay between search input and query before updating table.

    This mixin requires views to have:
    - table attribute (any table widget)
    - searchbox attribute (Search or custom search widget)

    Optional attributes:
    - clear_button: Button widget for "Reset filters" or "Clear filters"

    Configuration flags:
    - SEARCH_DELAY: Debounce delay in seconds (default: 0)

    Usage:
        class MyView(BaseLoggedInView, SearchableViewMixin):
            SEARCH_DELAY = 1

            searchbox = Search()  # or any search widget
            table = Table(...)
            clear_button = Button('Reset filters')  # optional
    """

    SEARCH_DELAY = 0  # Default debounce delay after last user input, if search is immediate

    # PatternFly loading indicators
    LOADING = (
        './/table[@aria-label="Loading"] | '  # legacy pattern
        './/div[contains(@class, "pf-v5-c-skeleton")] | '  # PF5 skeleton component
        './/td[contains(@class, "pf-v5-c-skeleton")]'  # PF5 skeleton table cells
    )
    TABLE_EMPTY_STATE = './/div[contains(@class, "-c-empty-state")]'

    # root locator for the search toolbar
    TOOLBAR = (
        '(.//div[contains(@class, "foreman-search-bar")] | '
        './/div[@data-ouia-component-id="table-toolbar"] | '
        './/div[contains(@class, "toolbar-pf")] | '
        './/div[@id="ins-primary-data-toolbar"])'
    )

    column_selector = Dropdown(
        locator=f'{TOOLBAR}//div[contains(@class, "ins-c-conditional-filter")]'
    )

    searchbox = Search()

    _reset_filters = PF5Button('Reset filters')
    _clear_filters = PF5Button('Clear filters')

    @property
    def table(self):
        """
        You must define the table widget in any View that inherits this
        """
        raise NotImplementedError

    def search(self, query):
        """Fill search component with the given query."""

        fill_widget = self.searchbox
        fill_value = query

        fill_widget.wait_displayed()
        current_value = fill_widget.read()

        if current_value == fill_value:
            self.logger.debug(
                'Search input field already matches the given query. Leaving it unchanged.'
            )
            return

        with self.ensure_table_reloads():
            fill_widget.search(fill_value)

        # TODO find better fix to dismiss the query dropdown, like click 'Esc'
        # if hasattr(self, 'title'):
        #     self.title.click()

        return self.table.read()

    def _wait_for_table_load(self, timeout):
        def _loaded():
            if self.browser.elements(self.LOADING):
                return False
            elif self.table.is_displayed:
                return True
            return False

        # Wait for "debounce" delay after search field input.
        if self.SEARCH_DELAY:
            time.sleep(self.SEARCH_DELAY)

        wait_for(_loaded, delay=0.2, num_sec=timeout)

    @contextmanager
    def ensure_table_reloads(self, timeout=10):
        yield
        self._wait_for_table_load(timeout)


class ListRemoveTab(SatSecondaryTab, SearchableViewMixin):
    """'List/Remove' tab, part of :class:`AddRemoveResourcesView`."""

    TAB_NAME = 'List/Remove'
    remove_button = Text(
        './/div[@data-block="list-actions"]//button[contains(@ng-click, "remove")]'
    )
    table = SatTable(
        locator='.//table', column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
    )

    def search(self, value):
        """Search for specific associated resource and return the results"""
        super().search(value)
        return self.table.read()

    def remove(self, value):
        """Remove specific associated resource"""
        super().search(value)
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


class AddTab(SatSecondaryTab, SearchableViewMixin):
    TAB_NAME = 'Add'
    add_button = Text('.//div[@data-block="list-actions"]//button[contains(@ng-click, "add")]')
    table = SatTable(
        locator='.//table', column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
    )

    def search(self, value):
        """Search for specific available resource and return the results"""
        super().search(value)
        return self.table.read()

    def add(self, value):
        """Associate specific resource"""
        super().search(value)
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


class NewAddRemoveResourcesView(View, SearchableViewMixin):
    status = PF5OUIASelect(component_id='select Status')
    remove_button = PF5OUIADropdown(component_id='repositoies-bulk-actions')
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
        super().search(value)
        return self.table.read()

    def add(self, value):
        """Associate specific resource"""
        self.select_status('Not added')
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
        self.select_status('Added')
        self.search(value)
        next(self.table.rows())[0].widget.fill(True)
        self.remove_button.item_select('Remove')

    def read(self):
        """Read all table values from both resource tables"""
        self.select_status('All')
        return self.table.read()


class AddRemoveSubscriptionsView(AddRemoveResourcesView):
    """A variant of :class:`AddRemoveResourcesView` for managing subscriptions.
    Subscriptions table has different structure - entity label is located in
    separate row apart from checkbox and other cells.
    """

    @View.nested
    class list_remove_tab(ListRemoveTab):
        table = SatSubscriptionsTable(
            locator='.//table', column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
        )

    @View.nested
    class add_tab(AddTab):
        table = SatSubscriptionsTable(
            locator='.//table', column_widgets={0: Checkbox(locator=".//input[@type='checkbox']")}
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
    fullscreen = Text(locator=".//button[@id='fullscreen-btn']")
    fullscreen_close = Text(
        locator="//button[@data-ouia-component-id='editor-modal-component-ModalBoxCloseButton']"
    )
    fullscreen_textarea = TextInput(locator="//div[@id='editor']/textarea")
    error = Text(".//div[@id='preview_error_toast']")
    editor = ACEEditor()

    def fill(self, values):
        if values.pop('fullscreen', False):
            fullscreen_data = values.pop('editor')
            self.fullscreen.click()
            self.fullscreen_textarea.fill(fullscreen_data)
            self.fullscreen_close.click()
        super().fill(values)


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

    ROOT = ".//div[@aria-label='bookmark-modal' or contains(@class, 'modal-dialog')]"

    title = Text(
        "//*[self::div[@data-block='modal-header'] or self::h4]"
        "[normalize-space(.) = 'Add Bookmark'"
        " or normalize-space(.) = 'Create Bookmark']"
    )
    name = TextInput(name='name')
    query = TextInput(name='query')
    error_message = Text(
        ".//span[@class='error-message' or (ancestor::div[contains(@class, 'pf-m-error')] and contains(@class, 'item-text'))]"
    )
    public = Checkbox(
        locator="//input[@data-ouia-component-id='isPublic-checkbox' or (@type='checkbox' and (@name='public' or @name='publik'))]"
    )
    submit = Text(
        ".//button[@data-ouia-component-id='submit-btn' or @type='submit' or @ng-click='ok()']"
    )
    cancel = Text(".//button[@data-ouia-component-id='cancel-btn' or normalize-space(.)='Cancel']")

    @property
    def is_displayed(self):
        return self.title.is_displayed


class TemplateInputItem(GenericRemovableWidgetItem):
    """Template Input item view"""

    remove_button = Text(".//a[contains(@class, 'remove_nested_fields')]")
    name = TextInput(locator=".//input[contains(@name, '[name]')]")
    required = Checkbox(locator=".//input[contains(@id, 'required')]")
    input_type = FilteredDropdown(locator=".//span[contains(@id, 'input_type')]")

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
