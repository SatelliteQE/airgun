from wait_for import wait_for
from widgetastic.widget import GenericLocatorWidget, Text, TextInput, View
from widgetastic_patternfly5.ouia import Switch as PF5OUIASwitch

from airgun.views.common import BaseLoggedInView


def _wait_for_spinner(widget):
    """Wait for any PF5 spinner to disappear from widget"""
    wait_for(
        lambda: (
            widget.is_displayed
            and not widget.browser.elements(
                ".//span[contains(@class, 'pf-v5-c-spinner')]", parent=widget
            )
        ),
        timeout=60,
        delay=1,
        logger=widget.logger,
    )


class AvailableRepositoryItem(GenericLocatorWidget):
    """The widget representation of Available repository item of an Available repository set.

    PF5 structure: each item is a <li class="pf-v5-c-data-list__item list-item-with-divider">
    """

    ENABLE_BUTTON = './/button[@aria-label="Enable"]'
    TEXT = './/div[contains(@class, "repository-text-md")]/span'

    @property
    def text(self):
        """Return the text representation of this repository (architecture + OS version)."""
        return self.browser.text(self.TEXT, parent=self).strip()

    def read(self):
        """Read this widget by returning its text representation."""
        return self.text

    def enable(self):
        """Enable this repository."""
        self.browser.click(self.ENABLE_BUTTON, parent=self)
        _wait_for_spinner(self.parent)


class AvailableRepositorySetWidget(GenericLocatorWidget):
    """The widget representation of Available repository set item.

    PF5 structure: each set is a <li class="pf-v5-c-data-list__item"> with a DataListToggle
    that expands to reveal individual repository items.
    """

    ITEM = AvailableRepositoryItem
    EXPAND_BUTTON = ".//div[contains(@class, 'pf-v5-c-data-list__toggle')]/button"
    NAME = ".//div[contains(@class, 'repository-name')]"
    LABEL = ".//div[contains(@class, 'repository-label')]"
    ITEMS = ".//li[contains(@class, 'list-item-with-divider')]"

    @property
    def expanded(self):
        """Check whether this repository set is expanded or not."""
        return (
            self.browser.get_attribute(
                'aria-expanded', self.browser.element(self.EXPAND_BUTTON, parent=self)
            )
            == 'true'
        )

    def expand(self):
        """Expand the repository set and wait until item texts are populated."""
        if not self.expanded:
            self.browser.click(self.EXPAND_BUTTON, parent=self)
        wait_for(
            lambda: bool(
                self.browser.elements(
                    ".//li[contains(@class, 'list-item-with-divider')]"
                    "//div[contains(@class, 'repository-text-md')]/span[normalize-space()]",
                    parent=self,
                )
            ),
            timeout=60,
            delay=1,
            logger=self.logger,
        )

    @property
    def name(self):
        """Return the name displayed for this repository item"""
        return self.browser.text(self.NAME, parent=self)

    @property
    def label(self):
        """Return the label displayed for this repository item"""
        return self.browser.text(self.LABEL, parent=self)

    @property
    def items(self):
        """Return all the items (available repositories) of this repository set."""
        if self.ITEM:
            self.expand()
            return [
                AvailableRepositoryItem(self, f'{self.ITEMS}[{index + 1}]')
                for index, _ in enumerate(self.browser.elements(self.ITEMS, parent=self))
            ]
        return []

    def read_items(self):
        """Read all the items (repositories) of this repository set"""
        return [item.text for item in self.items]

    def read(self):
        """Return the name and label of this repository."""
        return {'name': self.name, 'label': self.label}

    def enable(self, item):
        """Enable a repository of this repository set.

        :param str item: The arch and version (if available) of the repository.
        """
        for arch_version_item in self.items:
            if item == arch_version_item.text:
                arch_version_item.enable()
                break
        else:
            raise ValueError(f'Repository "{item}" was not found in repository set "{self.name}"')


class EnabledRepositoryWidget(AvailableRepositorySetWidget):
    """The widget representation of Enabled repository item."""

    ITEM = None
    DISABLE_BUTTON = './/button[@aria-label="Disable"]'

    def expand(self):
        """Expand the repository item and wait until the disable button is present."""
        if not self.expanded:
            self.browser.click(self.EXPAND_BUTTON, parent=self)
        wait_for(
            lambda: bool(self.browser.elements(self.DISABLE_BUTTON, parent=self)),
            timeout=60,
            delay=1,
            logger=self.logger,
        )

    def disable(self):
        """Disable this repository."""
        self.browser.click(self.DISABLE_BUTTON, parent=self)
        # Wait for React to start the loading state: the disable button is replaced by a spinner.
        wait_for(
            lambda: not self.browser.elements(self.DISABLE_BUTTON, parent=self),
            timeout=10,
            delay=0.5,
            logger=self.parent.logger,
        )
        _wait_for_spinner(self.parent)


class SearchCategorySelector(GenericLocatorWidget):
    """PF5 MenuToggle-based selector for the search category (Available/Enabled/Both).

    The toggle button is rendered inside .search-list-select-container; the menu is
    appended to document.body via Popper and located by its OUIA component id.
    """

    TOGGLE = ".//button[@data-ouia-component-id='search-list-select']"
    MENU_LOCATOR = "//div[@data-ouia-component-id='search-list-menu']"
    MENU_ITEM_LOCATOR = ".//button[contains(@class, 'pf-v5-c-menu__item')]"

    @property
    def current_selection(self):
        """Return the text of the currently selected category."""
        return self.browser.text(
            ".//span[contains(@class, 'pf-v5-c-menu-toggle__text')]",
            parent=self,
        )

    @property
    def is_open(self):
        """Check whether the dropdown menu is open."""
        return (
            self.browser.get_attribute(
                'aria-expanded', self.browser.element(self.TOGGLE, parent=self)
            )
            == 'true'
        )

    def open(self):
        if not self.is_open:
            self.browser.click(self.TOGGLE, parent=self)

    def close(self):
        if self.is_open:
            self.browser.click(self.TOGGLE, parent=self)

    def select(self, item):
        """Select a category from the body-appended Popper menu.

        :param str item: 'Available', 'Enabled', or 'Both'.
        """
        self.open()
        menu = self.browser.element(self.MENU_LOCATOR)
        for el in self.browser.elements(self.MENU_ITEM_LOCATOR, parent=menu):
            if self.browser.text(el).strip() == item:
                el.click()
                return
        raise ValueError(f'Category "{item}" not found in search category menu')

    def fill(self, item):
        """Select the given category if it differs from the current selection."""
        if item and self.current_selection != item:
            self.select(item)


class FilterTypeSelector(GenericLocatorWidget):
    """PF5 checkbox MenuToggle for filter dropdowns (e.g. filter-by-type, filter-by-product).

    Pass the OUIA component_id of the toggle button. The container root and the
    Popper-appended menu are derived from it by convention::

      root:  //div[button[@data-ouia-component-id='{component_id}']]
      menu:  //div[@data-ouia-component-id='{component_id}-menu']

    Sets the filter to exclusively the requested type, deselecting all others.
    Menu items are <label> elements; selection state is on the nested <input>.
    """

    MENU_ITEM_LOCATOR = ".//label[contains(@class, 'pf-v5-c-menu__item')]"
    ITEM_TEXT_LOCATOR = ".//span[contains(@class, 'pf-v5-c-menu__item-text')]"
    ITEM_CHECKBOX_LOCATOR = ".//input[contains(@class, 'pf-v5-c-check__input')]"

    def __init__(self, parent, component_id, **kwargs):
        locator = f"//div[button[@data-ouia-component-id='{component_id}']]"
        super().__init__(parent, locator, **kwargs)
        self._toggle = f".//button[@data-ouia-component-id='{component_id}']"
        self._menu_locator = f"//div[@data-ouia-component-id='{component_id}-menu']"

    @property
    def is_open(self):
        return (
            self.browser.get_attribute(
                'aria-expanded', self.browser.element(self._toggle, parent=self)
            )
            == 'true'
        )

    def open(self):
        if not self.is_open:
            self.browser.click(self._toggle, parent=self)

    def close(self):
        if self.is_open:
            self.browser.click(self._toggle, parent=self)

    def select(self, item):
        """Set the filter to only the given type, deselecting all others.

        :param str item: Label of the type to select (e.g. 'Kickstart', 'RPM').
        """
        self.open()
        menu = self.browser.element(self._menu_locator)
        for el in self.browser.elements(self.MENU_ITEM_LOCATOR, parent=menu):
            text = self.browser.text(
                self.browser.element(self.ITEM_TEXT_LOCATOR, parent=el)
            ).strip()
            checkbox = self.browser.element(self.ITEM_CHECKBOX_LOCATOR, parent=el)
            is_selected = checkbox.get_attribute('checked') is not None
            should_select = text.lower() == item.lower()
            if is_selected != should_select:
                el.click()
        self.close()


class RepositoryCategoryView(View):
    """The base class view that represent the Available or Enabled Repository

    Example html representation::

        <div class="available-repositories-container">
            <ul class="pf-v5-c-data-list">
                <li class="pf-v5-c-data-list__item">
                    ...
                </li>
            </ul>
        </div>
    """

    ITEMS = ".//ul[contains(@class, 'pf-v5-c-data-list')]/li"
    ITEM_WIDGET = None

    def items(self, name=None, label=None):
        items = []
        for index, _ in enumerate(self.browser.elements(self.ITEMS, parent=self)):
            item = self.ITEM_WIDGET(self, f'{self.ITEMS}[{index + 1}]')
            if (name is not None and item.name != name) or (
                label is not None and item.label != label
            ):
                continue
            items.append(item)
        return items

    def read(self):
        return [item.read() for item in self.items()]


class RedHatRepositoriesView(BaseLoggedInView):
    """The main Red Hat repositories view."""

    title = Text("//h1[contains(., 'Red Hat Repositories')]")
    search_category = SearchCategorySelector(
        "//div[button[@data-ouia-component-id='search-list-select']]"
    )
    search_box = TextInput(
        locator='//*[@id="redhatRepositoriesPage"]//following::input[@aria-label="Search input"]'
    )
    search_button = Text(
        '//*[@id="redhatRepositoriesPage"]//following::button[@aria-label="Search"]'
    )
    filter_by_product = FilterTypeSelector('filter-by-product')
    filter_by_type = FilterTypeSelector('filter-by-type')
    search_clear = Text(".//button[@aria-label='Reset search']")
    recommended_repos = PF5OUIASwitch('recommended-repos-switch')

    @View.nested
    class available(RepositoryCategoryView):
        ROOT = "//div[contains(@class, 'available-repositories-container')]"
        ITEM_WIDGET = AvailableRepositorySetWidget

    @View.nested
    class enabled(RepositoryCategoryView):
        ROOT = "//div[contains(@class, 'enabled-repositories-container')]"
        ITEM_WIDGET = EnabledRepositoryWidget

    def search(self, value, category='Available'):
        """Search repositories.

        :param str value: The string to search by.
        :param str category: The repository category to search, options: Available, Enabled, Both
        :return:
        """
        supported_categories = ['Available', 'Enabled', 'Both']
        if category not in supported_categories:
            raise ValueError(
                f'category "{category}" not supported, please choose from {supported_categories}'
            )
        if self.search_clear.is_displayed:
            self.search_clear.click()
        self.search_category.fill(category)
        self.search_box.fill(value)
        self.search_button.click()
        if category == 'Available':
            return self.available.read()
        elif category == 'Enabled':
            return self.enabled.read()
        else:
            return {'available': self.available.read(), 'enabled': self.enabled.read()}

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
