from widgetastic.exceptions import WidgetOperationFailed

from widgetastic.widget import (
    do_not_read_this_widget,
    GenericLocatorWidget,
    Text,
    TextInput,
    Widget
)
from widgetastic.xpath import quote
from widgetastic_patternfly import VerticalNavigation


class ItemsList(GenericLocatorWidget):
    """List with click-able elements. Part of :class:`MultiSelect` or jQuery
    drop-down.

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
    search_field = TextInput(
        locator="//input[@id='search' or @ng-model='table.searchTerm']")
    search_button = Text(
        "//button[contains(@type,'submit') or "
        "@ng-click='table.search(table.searchTerm)']"
    )

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
        do_not_read_this_widget()


class FilteredDropdown(GenericLocatorWidget):
    """Drop-down element with filtered functionality

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


class CustomParameter(Widget):
    """Name-Value paired input elements which can be added, edited or removed.

    Example html representation::

        <table class="table" id="global_parameters_table">
            <tr class="fields " id="new_os_parameter_row">
                <input placeholder="Name" type="text" ... id="..._name">
                <textarea id="new_os_parameter_value" placeholder="Value" ...>

    Locator example::

        //input[@placeholder='Name']
        //textarea[@placeholder='Value']

    """
    add_new_value = Text(".//a[contains(text(),'+ Add Parameter')]")
    new_parameter_name = TextInput(
        locator=".//input[@placeholder='Name' and not(@value)]")
    new_parameter_value = TextInput(
        locator=".//textarea[@placeholder='Value' and not(text())]")
    NAMES = (
        ".//tr[contains(@id, 'os_parameter')]/td/input[@placeholder='Name']")
    VALUE = (
        ".//table[contains(@id, 'parameters')]//tr"
        "/td[input[contains(@id, 'name')][contains(@value, '{}')]]"
        "/following-sibling::td//textarea"
    )

    def read(self):
        """Return a list of dictionaries. Each dictionary consists of name and
        value parameters
        """
        parameters = []
        for item in self.browser.elements(self.NAMES):
            name = self.browser.get_attribute('value', item)
            value = self.browser.text(self.VALUE.format(name))
            parameters.append({'name': name, 'value': value})
        return parameters

    def fill(self, values):
        """Create new parameter entity

        :param values: dictionary of name and value that should be assigned to
            new entity
        """
        self.add_new_value.click()
        self.new_parameter_name.fill(values['name'])
        self.new_parameter_value.fill(values['value'])


class SelectActionList(Widget):
    """Refer to 'Select Action' control which has simple list of actions to be
     selected from, once user click on the arrow button.

    Example html representation::

        <div data-block="item-actions" bst-feature-flag="custom_products"...>
            <button type="button" .... ng-click="toggleDropdown($event)">
                <ul>
                    <li role="menuitem" ng-hide="denied(...)" class="">

    Locator example::

        //div[@data-block='item-actions']

    """
    ROOT = "//div[@data-block='item-actions']"
    open_dropdown = Text(".//button[contains(@ng-click, 'toggleDropdown')]")
    ITEM = ".//li[not(contains(@style, 'display: none'))][contains(.,'%s')]"

    def fill(self, value):
        """Clicks on 'Select Action' control and choose necessary action

        :param value: string with name of action to be performed
        """
        self.open_dropdown.click()
        self.browser.click(
            self.browser.element(self.ITEM % value, parent=self))

    def read(self):
        """There is no need to read values for this widget"""
        do_not_read_this_widget()


class ConfirmationDialog(Widget):
    """Usual confirmation dialog with two buttons and close 'x' button in the
    right corner. Has nothing in common with javascript alert, confirm or
    prompt pop-ups.

    Example html representation::

        <div class="modal-content">
            <button type="button" class="close" ... ng-click="cancel()">
            <div class="modal-footer ng-scope">
                <button class="btn btn-danger" ng-click="ok()">
                <button class="btn ..." ng-click="cancel()"...>

    Locator example::

        //div[@class='modal-content']

    """
    ROOT = ".//div[@class='modal-content']"
    confirm_dialog = Text(".//button[contains(@ng-click, 'ok')]")
    cancel_dialog = Text(
        ".//button[contains(@ng-click, 'cancel') and contains(@class, 'btn')]")
    discard_dialog = Text(
        ".//button[contains(@ng-click, 'cancel') and @class='close']")

    def confirm(self):
        """Clicks on the positive outcome button like 'Remove', 'Ok', 'Yes'"""
        self.confirm_dialog.click()

    def cancel(self):
        """Clicks on the negative outcome button like 'Cancel' or 'No'"""
        self.cancel_dialog.click()

    def read(self):
        """Widgets has no fields to read"""
        do_not_read_this_widget()


class LCESelector(Widget):
    """Group of checkboxes that goes in a line one after another. Usually used
    to specify lifecycle environment

    Example html representation::

        <//ul[@class='path-list']>
            <li class="path-list-item ng-scope"...>
                <label class="path-list-item-label...>
                    <input type="checkbox"...>
            <li class="path-list-item ng-scope"...>
                <label class="path-list-item-label...>
                    <input type="checkbox"...>

    Locator example::

        //ul[@class='path-list']

    """
    ROOT = ".//ul[@class='path-list']"
    LABELS = "./li/label[contains(@class, path-list-item-label)]"
    CHECKBOX = (
        ".//input[@ng-model='item.selected'][parent::label[contains(., '{}')]]"
    )

    def checkbox_selected(self, locator):
        """Identify whether specific checkbox is selected or not"""
        return 'ng-not-empty' in self.browser.get_attribute('class', locator)

    def select(self, locator, value):
        """Select or deselect checkbox depends on the value passed"""
        value = bool(value)
        current_value = self.checkbox_selected(locator)
        if value == current_value:
            return False
        self.browser.element(locator).click()
        if self.checkbox_selected(locator) != value:
            raise WidgetOperationFailed(
                'Failed to set the checkbox to requested value.')
        return True

    def read(self):
        """Return a list of dictionaries. Each dictionary consists of name and
        value for each checkbox from the group
        """
        checkboxes = []
        for item in self.browser.elements(self.LABELS):
            name = self.browser.text(item)
            value = self.checkbox_selected(self.CHECKBOX.format(name))
            checkboxes.append({'name': name, 'value': value})
        return checkboxes

    def fill(self, value):
        """Assign value for specific checkbox from group

        :param value: dictionary that consist of single checkbox name and
            value that should be assigned to that checkbox
        """
        checkbox_name = list(value.keys())[0]
        checkbox_value = value[checkbox_name]
        checkbox_locator = self.CHECKBOX.format(checkbox_name)
        return self.select(checkbox_locator, checkbox_value)
