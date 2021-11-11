from cached_property import cached_property
from widgetastic.exceptions import NoSuchElementException
from widgetastic.widget import Checkbox
from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView
from airgun.widgets import SatTable


class ParentNodeNotFoundError(Exception):
    """Raise when not able to find a parent for a node item"""


class ReservedToSectionOnlyError(Exception):
    """Mainly raised when adding a child to a non section node"""


class NodeNotFoundError(Exception):
    """Raise when a node was not found"""


class SyncStatusTableNode:
    """Table row interface to implement a sync status table row tree node"""

    CHECKBOX = "./td/input[@type='checkbox']"
    RESULT_LINK = ".//a[not(contains(@class, 'hidden'))][not(contains(@class, 'progress'))]"
    RESULT_PROGRESS = ".//a[contains(@class, 'progress')]"
    SECTION_EXPANDER = "./td/span[contains(@class, 'expander')]"

    def __init__(self, parent=None, row=None):
        self.parent = parent
        self.row = row
        self.children = {}

    def __getitem__(self, name):
        """Return the child name"""
        return self.children[name]

    def __contains__(self, name):
        """Check child with name is exist in this node"""
        return name in self.children

    @property
    def browser(self):
        """Return the browser"""
        return self.row.browser

    @cached_property
    def id(self):
        """Return the id of this node"""
        return self.browser.get_attribute('id', self.row)

    @cached_property
    def is_root(self):
        """Return whether this node is root node"""
        return 'child-of' not in self.browser.get_attribute('class', self.row)

    def is_child_of(self, node):
        """Return whether this node is a child of node"""
        return f'child-of-{node.id}' in self.browser.get_attribute('class', self.row)

    @cached_property
    def name(self):
        """Return the name of this node, the node name is the text content of
        the first column."""
        return self.row[0].read()

    @property
    def result(self):
        """Return the result column content"""
        return self.row['RESULT'].read()

    @property
    def checkbox(self):
        """return the checkbox element of this row if exist"""
        try:
            checkbox = self.browser.element(self.CHECKBOX, parent=self.row)
        except NoSuchElementException:
            checkbox = None
        return checkbox

    @property
    def result_link(self):
        """Return the result link element of this row"""
        return self.browser.element(self.RESULT_LINK, parent=self.row)

    @property
    def progress(self):
        """Return the progress element of this row if exist"""
        try:
            progress = self.browser.element(self.RESULT_PROGRESS, parent=self.row)
        except NoSuchElementException:
            progress = None
        return progress

    @property
    def expander(self):
        """Return the expander element of this row if exist"""
        try:
            expander = self.browser.element(self.SECTION_EXPANDER, parent=self.row)
        except NoSuchElementException:
            expander = None
        return expander

    @property
    def expanded(self):
        """Return True in case this row is expanded"""
        if 'expanded' in self.browser.get_attribute('class', self.row):
            return True
        return False

    def expand(self):
        """Expand this node"""
        if self.is_section and not self.expanded:
            self.browser.click(self.expander)

    @cached_property
    def is_section(self):
        """Return whether this row is a section, a row is a section if has
        expander.
        """
        return bool(self.expander)

    def add_child(self, node):
        """Add a child node to this node"""
        if not self.is_section:
            # we cannot add a node to a non section node
            raise ReservedToSectionOnlyError('Adding node to a non section one is prohibited')
        if node.parent is not None:
            raise ValueError('Child Node already has parent')

        node.parent = self
        self.children[node.name] = node

    def read(self):
        """Read this node and sub nodes if exist"""
        if self.is_section:
            data = {}
            # ensure expanded before read
            self.expand()
            for child_name, child_node in self.children.items():
                data[child_name] = child_node.read()
        else:
            data = self.row.read()
        return data

    def select(self, value):
        """Select or un-select if checkbox is in the row, the checkbox exist
        only for repository row.
        """
        checkbox = self.checkbox
        if checkbox:
            checked = self.browser.get_attribute('checked', checkbox)
            if (value and not checked) or (not value and checked):
                self.browser.click(checkbox)

    def fill(self, values):
        """Fill the node and sub nodes with values"""
        if self.is_section:
            self.expand()
            if values:
                for key, value in values.items():
                    child_node = self.children[key]
                    child_node.fill(value)
        else:
            self.select(values)


class SyncStatusTable(SatTable):
    """This is a representation of a tree view with columns realized as a
    table. The first column is the tree expander where root item is the
    product. Each item and sub items located in their own table row.

    Tree representation of the first column example:

        - Red Hat Enterprise Linux Server
            - 7Server
                - x86_64
                    - [ ] Red Hat Enterprise Linux 7 Server RPMs x86_64
                        7Server
            - Red Hat Satellite Tools 6.2 for RHEL 7 Server RPMs x86_64
        - zoo custom product
            - [ ] zoo custom repo
        - an other custom repo
            - [ ] an other custom repo
    """

    @cached_property
    def nodes(self):
        """Return the tree nodes representation of this table"""
        nodes = {}
        last_section_node = None
        for row_index, row in enumerate(self):
            node = SyncStatusTableNode(row=row)
            if node.is_root:
                # Root nodes are essentially product names.
                node.expand()
                nodes[node.name] = node
                last_section_node = node
            else:
                # go throw last node parents to find the parent, if that parent
                # is found set it as last section parent.
                parent_node = last_section_node
                while parent_node:
                    if node.is_child_of(parent_node):
                        parent_node.add_child(node)
                        if node.is_section:
                            node.expand()
                            last_section_node = node
                        else:
                            last_section_node = parent_node
                        break
                    parent_node = parent_node.parent
                else:
                    # We have not found a parent for this node,
                    # this has not to happen, but in any case raise exception
                    raise ParentNodeNotFoundError(
                        f'Parent node for row index = {row_index} not found'
                    )
        return nodes

    def read(self):
        """Return a dict with nodes properties"""
        data = {}
        for name, node in self.nodes.items():
            data[name] = node.read()
        return data

    def fill(self, values):
        """Fill the node and sub nodes, mainly select or un-select the
        repositories.
        """
        if not values:
            return
        nodes = self.nodes
        for key, value in values.items():
            nodes[key].fill(value)

    def get_node_from_path(self, node_path):
        """Return a node from it's path representation

        :param node_path: a list or tuple representing the path to a node, for
            example: ('product1', 'repo1')
        :return: SyncStatusTableNode
        """
        parent_node = self.nodes
        node = None
        for name in node_path:
            if name and name in parent_node:
                node = parent_node[name]
                parent_node = node
        if node and node.name != node_path[-1]:
            raise NodeNotFoundError(f'Target node "{node_path}" not found')
        return node


class SyncStatusView(BaseLoggedInView):
    title = Text("//h2[contains(., 'Sync Status')]")
    collapse_all = Text(".//a[@id='collapse_all']")
    expand_all = Text(".//a[@id='expand_all']")
    select_none = Text(".//a[@id='select_none']")
    select_all = Text(".//a[@id='select_all']")
    active_only = Checkbox(id='sync_toggle')
    table = SyncStatusTable(".//table[@id='products_table']")
    synchronize_now = Text(".//form/input[@type='submit']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
