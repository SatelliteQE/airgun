from wait_for import wait_for
from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import Text, Widget
from widgetastic_patternfly5 import Button as PF5Button
from widgetastic_patternfly5.components.table import PatternflyTable, PatternflyTableRow
from widgetastic_patternfly5.ouia import Switch as PF5OUIASwitch

from airgun.views.common import BaseLoggedInView


class NodeNotFoundError(Exception):
    """Raise when a node was not found"""


class SyncStatusTreeRow(PatternflyTableRow):
    """A row in the PF5 tree table that supports aria-based tree attributes.

    In the Sync Status tree table all ``<tr>`` rows live inside a single
    ``<tbody>``.  Child rows that are collapsed carry the ``hidden``
    attribute.  The first cell of each row is a ``<th>`` (not ``<td>``),
    containing the tree toggle, checkbox and name.
    """

    ROW_TOGGLE = ".//span[contains(@class, 'pf-v5-c-table__toggle')]//button"
    NAME_SPAN = ".//div[contains(@class, 'pf-v5-c-table__tree-view-text')]//span[@role='button']"
    CHECKBOX = ".//input[@type='checkbox']"
    PROGRESS_BAR = ".//div[contains(@class, 'pf-v5-c-progress')]"

    @property
    def is_hidden(self):
        """Return True if this row has the hidden attribute (collapsed child)."""
        return self.browser.get_attribute('hidden', self) is not None

    @property
    def aria_level(self):
        """Return the tree nesting level of this row (1 = root product)."""
        level = self.browser.get_attribute('aria-level', self)
        return int(level) if level else None

    @property
    def is_expandable(self):
        """Return whether this row can be expanded (has child nodes).

        Leaf nodes have ``aria-setsize="0"``.
        """
        setsize = self.browser.get_attribute('aria-setsize', self)
        return setsize is not None and int(setsize) > 0

    @property
    def is_expanded(self):
        """Return whether this row is currently expanded."""
        expanded = self.browser.get_attribute('aria-expanded', self)
        return expanded == 'true'

    @property
    def name(self):
        """Return the name text from the clickable span inside the tree cell."""
        try:
            name_el = self.browser.element(self.NAME_SPAN, parent=self)
            return self.browser.text(name_el).strip()
        except NoSuchElementException:
            return None

    def expand(self):
        """Expand this row if it is expandable and not already expanded."""
        if self.is_expandable and not self.is_expanded:
            toggle = self.browser.element(self.ROW_TOGGLE, parent=self)
            self.browser.click(toggle)

    def collapse(self):
        """Collapse this row if it is expandable and currently expanded."""
        if self.is_expandable and self.is_expanded:
            toggle = self.browser.element(self.ROW_TOGGLE, parent=self)
            self.browser.click(toggle)

    @property
    def checkbox(self):
        """Return the checkbox element for this row, or None if not present."""
        try:
            return self.browser.element(self.CHECKBOX, parent=self)
        except NoSuchElementException:
            return None

    def select(self, value=True):
        """Select or deselect this row's checkbox."""
        cb = self.checkbox
        if cb is None:
            return
        checked = self.browser.get_attribute('checked', cb) is not None
        if bool(value) != checked:
            self.browser.click(cb)

    @property
    def has_progress(self):
        """Return True if this row shows a sync progress bar."""
        try:
            self.browser.element(self.PROGRESS_BAR, parent=self)
            return True
        except NoSuchElementException:
            return False

    @property
    def result(self):
        """Return the text content of the Progress / Result column."""
        return self['Progress / Result'].read()


class SyncStatusTreeTable(PatternflyTable):
    """PF5 tree table for Sync Status page.

    The table has ``role="treegrid"`` with a single ``<tbody>`` containing
    all ``<tr>`` rows.  Collapsed children carry a ``hidden`` attribute.
    Each row has ``aria-level``, ``aria-setsize``, ``aria-posinset``, and
    ``aria-expanded`` attributes describing the tree structure.

    ``read()`` returns a nested dict::

        {
            product_name: {
                repo_name: 'Syncing complete'
            }
        }

    or for deeper hierarchies (RH products)::

        {
            product_name: {
                version: {
                    arch: {
                        repo_name: 'Syncing complete'
                    }
                }
            }
        }
    """

    ROWS = './tbody/tr'
    HEADERS = './thead/tr/th|./thead/tr/td'
    EXPAND_ALL_BUTTON = './thead//th[contains(@class, "pf-v5-c-table__toggle")]//button'
    Row = SyncStatusTreeRow

    def _visible_rows(self):
        """Yield only rows that are not hidden (i.e. not collapsed children)."""
        for row in self:
            if not row.is_hidden:
                yield row

    def _expand_all(self):
        """Expand all tree nodes using the header expand/collapse toggle.

        Only clicks the toggle when hidden rows exist (tree is partially or
        fully collapsed).  After clicking, waits for all hidden rows to
        become visible.
        """
        hidden_locator = './tbody/tr[@hidden]'
        if not self.browser.elements(hidden_locator, parent=self):
            return
        try:
            toggle = self.browser.element(self.EXPAND_ALL_BUTTON, parent=self)
        except NoSuchElementException:
            return
        self.browser.click(toggle)
        wait_for(
            lambda: not self.browser.elements(hidden_locator, parent=self),
            timeout=10,
            delay=0.5,
        )

    def read(self):
        """Return a nested dict built from the tree hierarchy.

        Expands all nodes first, then walks visible rows using
        ``aria-level`` to reconstruct the tree.  Leaf rows (``aria-setsize="0"``)
        store their Progress / Result text as the value.
        """
        self._expand_all()
        result = {}
        # Stack tracks (level, dict_ref) for the current nesting path
        stack = [(0, result)]
        for row in self._visible_rows():
            name = row.name
            if name is None:
                continue
            level = row.aria_level or 1
            # Pop stack back to the parent of this level
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent_dict = stack[-1][1] if stack else result
            if row.is_expandable:
                row.expand()
                child_dict = {}
                parent_dict[name] = child_dict
                stack.append((level, child_dict))
            else:
                parent_dict[name] = row.result
        return result

    def get_row_by_name(self, name):
        """Find and return the first visible row matching the given name.

        :param name: the text to match in the Name column
        :return: SyncStatusTreeRow
        :raises NodeNotFoundError: if no row matches
        """
        for row in self._visible_rows():
            if row.name == name:
                return row
        raise NodeNotFoundError(f'Row with name "{name}" not found')

    def get_node_from_path(self, node_path):
        """Navigate the tree to find a node by its path.

        Expands parent nodes as needed to reveal child rows.

        :param node_path: a list or tuple representing the path to a node,
            e.g. ('product1', 'repo1')
        :return: SyncStatusTreeRow
        :raises NodeNotFoundError: if the target node is not found
        """
        non_none_path = [name for name in node_path if name is not None]
        current_row = None
        for i, name in enumerate(non_none_path):
            is_last = i == len(non_none_path) - 1
            if current_row is not None:
                current_row.expand()
            found = False
            for row in self._visible_rows():
                if row.name == name:
                    current_row = row
                    found = True
                    break
            if not found:
                if is_last:
                    raise NodeNotFoundError(f'Node "{name}" not found in path {node_path}')
                # Intermediate level not present in tree, skip it
        return current_row


class SelectAllDropdown(Widget):
    """Split-button checkbox dropdown for Select All / Select None."""

    ROOT = './/div[@data-ouia-component-id="tree-selection-checkbox"]'
    CHECKBOX = './/input[@aria-label="Select all"]'
    TOGGLE_BUTTON = './/button[contains(@class, "pf-v5-c-dropdown__toggle-button")]'
    SELECT_NONE = './/button[@data-ouia-component-id="select-none"]'
    SELECT_ALL = './/button[@data-ouia-component-id="select-all"]'

    def _open_dropdown(self):
        """Open the dropdown menu."""
        toggle = self.browser.element(self.TOGGLE_BUTTON, parent=self)
        self.browser.click(toggle)

    def select_all(self):
        """Select all repositories."""
        self._open_dropdown()
        btn = self.browser.element(self.SELECT_ALL, parent=self)
        self.browser.click(btn)

    def select_none(self):
        """Deselect all repositories."""
        self._open_dropdown()
        btn = self.browser.element(self.SELECT_NONE, parent=self)
        self.browser.click(btn)

    @property
    def is_displayed(self):
        try:
            self.browser.element(self.CHECKBOX, parent=self)
            return True
        except NoSuchElementException:
            return False


class SyncStatusView(BaseLoggedInView):
    title = Text('//h1[@data-ouia-component-id="sync-status-title"]')

    # Toolbar
    selection_dropdown = SelectAllDropdown()
    show_syncing_only = PF5OUIASwitch('show-syncing-only-switch')
    synchronize = PF5Button(locator='//button[@data-ouia-component-id="sync-button"]')

    # Tree table
    table = SyncStatusTreeTable(locator='.//table[@data-ouia-component-id="sync-status-table"]')

    @property
    def is_displayed(self):
        return self.title.is_displayed
