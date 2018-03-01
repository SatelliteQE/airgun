from widgetastic.exceptions import DoNotReadThisWidget
from widgetastic.widget import GenericLocatorWidget, Text, TextInput, Widget
from widgetastic.xpath import quote
from widgetastic_patternfly import VerticalNavigation


class ItemsList(GenericLocatorWidget):
    """List with clickable elements. Part of :class:`MultiSelect` or jQuery
    dropdown.

    Example html representation::

        <ul class="ms-list" tabindex="-1">

    Locator example::

        //ul[@class='ms-list']

    """
    ITEM = "./li[not(contains(@style, 'display: none'))][contains(.,'%s')]"
    ITEMS = "./li[not(contains(@style, 'display: none'))]"

    def read(self):
        """Return a list of strings representing elements in the
        :class:`ItemsList`."""
        return [
            el.text for el in self.browser.elements(self.ITEMS, parent=self)]

    def fill(self, value):
        """Clicks on element inside the list.

        :param value: string with element name
        """
        self.browser.click(
            self.browser.element(self.ITEM % value, parent=self))


class MultiSelect(GenericLocatorWidget):
    """Typical two-pane multiselect jQuery widget. Allows to move items from
    list of ``unassigned`` entities to list of ``assigned`` ones and vice
    versa.

    Examples on UI::

        Hosts -> Architectures -> any -> Operating Systems
        Hosts -> Operating Systems -> any -> Architectures

    Example html representation::

        <div class="ms-container" id="ms-operatingsystem_architecture_ids">

    Locator examples::

        //div[@id='ms-operatingsystem_architecture_ids']
        id='ms-operatingsystem_architecture_ids'

    """
    filter = TextInput(locator=".//input[@class='ms-filter']")
    unassigned = ItemsList("./div[@class='ms-selectable']/ul")
    assigned = ItemsList("./div[@class='ms-selection']/ul")

    def __init__(self, parent, locator=None, id=None, logger=None):
        """Supports initialization via ``locator=`` or ``id=``"""
        if locator and id or not locator and not id:
            raise TypeError('Please specify either locator or id')
        locator = locator or ".//div[@id='{}']".format(id)
        super(MultiSelect, self).__init__(parent, locator, logger)

    def fill(self, values):
        """Read current values, find the difference between current and passed
        ones and fills the widget accordingly.

        :param values: dict with keys ``assigned`` and/or ``unassigned``,
            containing list of strings, representing item names
        """
        current = self.read()
        to_add = set(values.get('assigned', ())) - set(current['assigned'])
        to_remove = set(
            values.get('unassigned', ())) - set(current['unassigned'])
        if not to_add and not to_remove:
            return False
        if to_add:
            for value in to_add:
                self.filter.fill(value)
                self.unassigned.fill(value)
        if to_remove:
            for value in to_remove:
                self.assigned.fill(value)
        return True

    def read(self):
        """Returns a dict with current lists values."""
        return {
            'unassigned': self.unassigned.read(),
            'assigned': self.assigned.read(),
        }


class Search(Widget):
    search_field = TextInput(id='search')
    search_button = Text("//button[contains(@type,'submit')]")

    def fill(self, value):
        return self.search_field.fill(value)

    def read(self):
        return self.search_field.read()

    def search(self, value):
        # Entity lists with 20+ elements may scroll page a bit and search field
        # will appear out of screen. For some reason, clicking search button
        # will have no effect in such case. Scrolling to search field just in
        # case
        # fixme: needs further investigation and implementation on different
        # layer, maybe in self.browser.element
        self.browser.selenium.execute_script(
            'arguments[0].scrollIntoView(false);',
            self.browser.element(self.search_field.locator),
        )
        self.fill(value)
        self.search_button.click()


class SatVerticalNavigation(VerticalNavigation):
    """The Patternfly Vertical navigation."""
    CURRENTLY_SELECTED = './/li[contains(@class, "active")]/a/span'


class ContextSelector(Widget):
    CURRENT_ORG = '//li[@id="organization-dropdown"]/a'
    CURRENT_LOC = '//li[@id="location-dropdown"]/a'
    ORG_LOCATOR = '//li[@id="organization-dropdown"]/ul/li/a[contains(.,{})]'
    LOC_LOCATOR = '//li[@id="location-dropdown"]/ul/li/a[contains(.,{})]'

    def select_org(self, org_name):
        l1e = self.browser.element(self.CURRENT_ORG)
        self.browser.move_to_element(l1e)
        self.browser.click(l1e)
        l2e = self.browser.element(self.ORG_LOCATOR.format(quote(org_name)))
        self.browser.execute_script(
            "arguments[0].click();",
            l2e,
        )
        self.browser.plugin.ensure_page_safe()

    def current_org(self):
        return self.browser.text(self.CURRENT_ORG)

    def select_loc(self, loc_name):
        l1e = self.browser.element(self.CURRENT_LOC)
        self.browser.move_to_element(l1e)
        self.browser.click(l1e)
        l2e = self.browser.element(self.LOC_LOCATOR.format(quote(loc_name)))
        self.browser.execute_script(
            "arguments[0].click();",
            l2e,
        )
        self.browser.plugin.ensure_page_safe()

    def current_loc(self):
        return self.browser.text(self.CURRENT_LOC)

    def read(self):
        """As reading organization and location is not atomic operation: needs
        mouse moves, clicks, etc, and this widget is included in every view -
        calling :meth:`airgun.views.common.BaseLoggedInView.read` for any view
        will trigger reading values of :class:`ContextSelector`. Thus, to avoid
        significant performance degradation it should not be readable.

        Use :meth:`current_org` and :meth:`current_loc` instead.
        """
        raise DoNotReadThisWidget


class FilteredDropdown(GenericLocatorWidget):
    """Dropdown element with filtered functionality

    Example html representation::

        <div class="select2-container form-control" id="s2id_subnet_boot_mode">

    Locator example::

        id=subnet_boot_mode
        id=s2id_subnet_ipam

    """
    selected_value = Text("./a/span[contains(@class, 'chosen')]")
    open_filter = Text("./a/span[contains(@class, 'arrow')]")
    filter_criteria = TextInput(locator="//div[@id='select2-drop']//input")
    filter_content = ItemsList(
        "//div[not(contains(@style, 'display: none')) and "
        "@id='select2-drop']/ul"
    )

    def __init__(self, parent, id=None, logger=None):
        """Supports initialization via ``id=`` only"""
        if not id:
            raise TypeError('Please specify id of select list element')
        locator = ".//div[contains(@id, '{}')]".format(id)
        super(FilteredDropdown, self).__init__(parent, locator, logger)

    def read(self):
        """Return drop-down selected item value"""
        return self.browser.text(self.selected_value)

    def fill(self, value):
        """Select specific item from the drop-down

        :param value: string with item value
        """
        self.open_filter.click()
        self.filter_criteria.fill(value)
        self.filter_content.fill(value)
