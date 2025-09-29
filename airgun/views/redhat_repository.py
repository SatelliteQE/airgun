from wait_for import wait_for
from widgetastic.widget import GenericLocatorWidget, Text, TextInput, View

from airgun.views.common import BaseLoggedInView
from airgun.widgets import (
    ActionsDropdown,
)


def _wait_for_spinner(widget):
    """Wait for any spinner to disappear from widget"""
    wait_for(
        lambda: widget.is_displayed
        and not widget.browser.elements(".//div[contains(@class, 'spinner')]", parent=widget),
        timeout=60,
        delay=1,
        logger=widget.logger,
    )


class AvailableRepositoryItem(GenericLocatorWidget):
    """The widget representation of Available repository item of an Available repository set."""

    ENABLE_BUTTON = './/button'
    TEXT = './/span'

    @property
    def text(self):
        """Return the text representation of this repository eg: architecture + OS version if
        available.
        """
        return self.browser.text(self.TEXT, parent=self)

    def read(self):
        """Read this widget by return it's text representation."""
        return self.text

    def enable(self):
        """Enable this repository."""
        self.browser.click(self.ENABLE_BUTTON, parent=self)
        _wait_for_spinner(self.parent)


class AvailableRepositorySetWidget(GenericLocatorWidget):
    """The widget representation of Available repository set item."""

    ITEM = AvailableRepositoryItem
    EXPAND_BUTTON = ".//div[contains(@class, 'expand')]"
    NAME = ".//div[contains(@class, 'item-heading')]"
    LABEL = ".//div[contains(@class, 'item-text')]"
    ITEMS = ".//div[contains(@class, 'list-item-with-divider')]"

    @property
    def expand_button(self):
        """Return the expand button element."""
        return self.browser.element(self.EXPAND_BUTTON, parent=self)

    @property
    def expanded(self):
        """Check whether this repository set is expanded or not."""
        return 'active' in self.browser.get_attribute('class', self.expand_button)

    def expand(self):
        """Expand the repository set item section."""
        if not self.expanded:
            self.browser.click(self.EXPAND_BUTTON, parent=self)
            _wait_for_spinner(self.parent)

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
        self.expand()
        for arch_version_item in self.items:
            if item == arch_version_item.text:
                arch_version_item.enable()
                break
        else:
            raise ValueError(f'Repository "{item}" was not found in repository set "{self.name}"')


class EnabledRepositoryWidget(AvailableRepositorySetWidget):
    """The widget representation of Enabled repository item."""

    ITEM = None
    DISABLE_BUTTON = './/button'

    def disable(self):
        """Disable this repository."""
        self.browser.click(self.DISABLE_BUTTON, parent=self)
        _wait_for_spinner(self.parent)


class RepositorySearchCategory(ActionsDropdown):
    """The category search selector, eg: Available, Enabled or Both."""

    button = Text('./button')

    def fill(self, item):
        """Selects Search Repository Category."""
        if item and self.button.is_displayed and self.button.text != item:
            self.select(item)


class RepositorySearchTypes(ActionsDropdown):
    """Repository content types dropdown for repository search."""

    button = Text('./button')

    def close(self):
        """Closes the dropdown list."""
        if self.is_open:
            self.dropdown.click()

    @property
    def selected_items(self):
        """Returns a list of all dropdown selected items as strings."""
        return [
            self.browser.text(el)
            for el in self.browser.elements(self.ITEMS_LOCATOR, parent=self)
            if el.get_attribute('aria-selected') == 'true'
        ]

    def select(self, items):
        """Selects Search Repository content types.

        :param items: The Repository content types required
        """
        selected_items = self.selected_items
        available_items = self.items
        self.open()
        for item in available_items:
            if (item in items and item not in selected_items) or (
                item not in items and item in selected_items
            ):
                self.browser.element(self.ITEM_LOCATOR.format(item), parent=self).click()
        self.close()

    def fill(self, items):
        """Selects Search Repository content types"""
        if self.button.is_displayed and set(self.selected_items) != set(items):
            self.select(items)


class RepositoryCategoryView(View):
    """The base class view that represent the Available or Enabled Repository

    Example html representation::

        <div class="enabled-repositories-container">
            <h2>Enabled Repositories</h2>
            <div class="list-group list-view-pf list-view-pf-view">
                <div class="sticky-pagination sticky-pagination-grey">
                <div class="list-group-item list-view-pf-stacked">
                    ...
                </div>
            </div>
    """

    ITEMS = "./div/div[contains(@class, 'list-group-item')]"
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
    search_category = RepositorySearchCategory(".//div[button[@id='search-list-select']]")
    search_box = TextInput(
        locator='//*[@id="redhatRepositoriesPage"]//following::input[@aria-label="Search input"]'
    )
    search_button = Text(
        '//*[@id="redhatRepositoriesPage"]//following::button[@aria-label="Search"]'
    )
    search_types = RepositorySearchTypes(".//div[button[@data-id='formControlsSelectMultiple']]")
    search_clear = Text(".//span[@class = 'fa fa-times']")
    recommended_repos = Text(".//div[contains(@class, 'bootstrap-switch wrapper')]")

    @View.nested
    class available(RepositoryCategoryView):
        ROOT = "//div[contains(@class, 'available-repositories-container')]"
        ITEM_WIDGET = AvailableRepositorySetWidget

    @View.nested
    class enabled(RepositoryCategoryView):
        ROOT = "//div[contains(@class, 'enabled-repositories-container')]"
        ITEM_WIDGET = EnabledRepositoryWidget

    def search(self, value, category='Available', types=None):
        """Search repositories.

        :param str value: The string to search by.
        :param str category: The repository category to search, options: Available, Enabled, Both
        :param list[str] types: (optional) The repository content types to refine the search
        :return:
        """
        if types is None:
            types = []
        supported_categories = ['Available', 'Enabled', 'Both']
        if category not in supported_categories:
            raise ValueError(
                f'category "{category}" not supported, please choose from {supported_categories}'
            )
        if self.search_clear.is_displayed:
            self.search_clear.click()
        self.search_category.fill(category)
        self.search_types.fill(types)
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
