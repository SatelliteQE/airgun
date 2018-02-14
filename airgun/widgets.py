from widgetastic.exceptions import NoSuchElementException
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, TextInput, Widget
from widgetastic.xpath import quote


class ResourceList(Widget):
    filter = TextInput(locator=ParametrizedLocator(
        "{@parent_locator}//input[@class='ms-filter']"))

    ITEM_FROM = ParametrizedLocator(
        "{@parent_locator}/div[@class='ms-selectable']"
        "//li[not(contains(@style, 'display: none'))]/span[contains(.,'%s')]"
    )
    ITEM_TO = ParametrizedLocator(
        "{@parent_locator}/div[@class='ms-selection']"
        "//li[not(contains(@style, 'display: none'))]/span[contains(.,'%s')]"
    )
    LIST_FROM = ParametrizedLocator(
        "{@parent_locator}/div[@class='ms-selectable']"
        "//li[not(contains(@style, 'display: none'))]"
    )
    LIST_TO = ParametrizedLocator(
        "{@parent_locator}/div[@class='ms-selection']"
        "//li[not(contains(@style, 'display: none'))]"
    )

    def __init__(self, parent, parent_entity, affected_entity, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.parent_entity = parent_entity.lower()
        self.affected_entity = affected_entity.lower()
        self.parent_locator = (
            "//div[contains(@id, 'ms-{}') and "
            "contains(@id, '{}_ids')]".format(
                self.parent_entity, self.affected_entity)
        )

    def _filter_value(self, value):
        self.filter.fill(value)

    def assign_resource(self, values):
        for value in values:
            self._filter_value(value)
            self.browser.click(
                self.browser.element(self.ITEM_FROM.locator % value))

    def unassign_resource(self, values):
        for value in values:
            self._filter_value(value)
            self.browser.click(
                self.browser.element(self.ITEM_TO.locator % value))

    def fill(self, values):
        if values['operation'] == 'Add':
            self.assign_resource(values['values'])
        if values['operation'] == 'Remove':
            self.unassign_resource(values['values'])

    def read(self):
            return {
                'free': [
                    el.text for el in self.browser.elements(self.LIST_FROM)],
                'assigned': [
                    el.text for el in self.browser.elements(self.LIST_TO)]
            }


class Search(Widget):
    search_field = TextInput(id='search')
    search_button = Text("//button[contains(@type,'submit')]")
    default_result_locator = Text("//a[contains(., '%s')]")

    def fill(self, value):
        self.search_field.fill(value)

    def read(self, value, result_locator=None):
        if result_locator is None:
            result_locator = self.default_result_locator
        return self.browser.element(result_locator.locator % value).text

    def search(self, value, result_locator=None):
        self.fill(value)
        self.search_button.click()
        return self.read(value, result_locator)


class HorizontalNavigation(Widget):
    """The Patternfly style horizontal top menu.

    Use :py:meth:`select` to select the menu items. This takes IDs.
    """
    LEVEL_1 = (
        '//ul[contains(@class, "navbar-menu")]/li/a[normalize-space(.)={}]')
    LEVEL_2 = (
        '//ul[contains(@class, "navbar-menu")]/li[./a[normalize-space(.)={}]'
        ' and contains(@class, "open")]/ul/li/a[normalize-space(.)={}]')
    ACTIVE = (
        '//ul[contains(@class, "navbar-menu")]/li[contains(@class, "active")]'
        '/a')

    def select(self, level1, level2=None):
        l1e = self.browser.element(self.LEVEL_1.format(quote(level1)))
        if not level2:
            # Clicking only the main menu item
            self.browser.click(l1e)
            return

        # Hover on the menu on the right spot
        self.browser.move_to_element(l1e)
        l2e = self.browser.wait_for_element(
            self.LEVEL_2.format(quote(level1), quote(level2)))
        self.browser.click(l2e)

    @property
    def currently_selected(self):
        try:
            # Currently we cannot figure out the submenu selection as it is not
            # marked in the UI
            return [self.browser.text(self.ACTIVE)]
        except NoSuchElementException:
            return []


class ContextSelector(Widget):
    TOP_SWITCHER = (
        '//ul[contains(@class, "navbar-menu")]/'
        'li[contains(@class,"org-switcher")]/a'
    )
    ORG_LOCATOR = '//ul[contains(@class, "org-submenu")]/li/a[contains(.,{})]'
    LOC_LOCATOR = '//ul[contains(@class, "loc-submenu")]/li/a[contains(.,{})]'
    SELECT_CURRENT_ORG = (
        '(//li[contains(@class,"org-switcher")]//li'
        '/a[@data-toggle="dropdown"])[1]'
    )
    SELECT_CURRENT_LOC = (
        '(//li[contains(@class,"org-switcher")]//li'
        '/a[@data-toggle="dropdown"])[2]'
    )
    FETCH_CURRENT_ORG = '//li[contains(@class, "org-menu")]/a'
    FETCH_CURRENT_LOC = '//li[contains(@class, "loc-menu")]/a'

    def select_org(self, org_name):
        l1e = self.browser.element(self.TOP_SWITCHER)
        self.browser.move_to_element(l1e)
        self.browser.click(l1e)
        l2e = self.browser.element(self.SELECT_CURRENT_ORG)
        self.browser.move_to_element(l2e)
        l3e = self.browser.element(self.ORG_LOCATOR.format(quote(org_name)))
        self.browser.execute_script(
            "arguments[0].click();",
            l3e,
        )
        self.browser.plugin.ensure_page_safe()

    def current_org(self):
        l1e = self.browser.element(self.TOP_SWITCHER)
        self.browser.move_to_element(l1e)
        current_org = self.browser.text(self.FETCH_CURRENT_ORG)
        self.browser.click(l1e)
        self.browser.move_by_offset(-150, -150)
        return current_org

    def select_loc(self, loc_name):
        l1e = self.browser.element(self.TOP_SWITCHER)
        self.browser.move_to_element(l1e)
        self.browser.click(l1e)
        l2e = self.browser.element(self.SELECT_CURRENT_LOC)
        self.browser.move_to_element(l2e)
        l3e = self.browser.element(self.LOC_LOCATOR.format(quote(loc_name)))
        self.browser.execute_script(
            "arguments[0].click();",
            l3e,
        )
        self.browser.plugin.ensure_page_safe()

    def current_loc(self):
        l1e = self.browser.element(self.TOP_SWITCHER)
        self.browser.move_to_element(l1e)
        current_loc = self.browser.text(self.FETCH_CURRENT_LOC)
        self.browser.click(l1e)
        self.browser.move_by_offset(-150, -150)
        return current_loc
