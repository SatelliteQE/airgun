import time

from cached_property import cached_property
from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from widgetastic.exceptions import NoSuchElementException, WidgetOperationFailed
from widgetastic.widget import (
    Checkbox,
    ClickableMixin,
    GenericLocatorWidget,
    ParametrizedLocator,
    Select,
    Table,
    Text,
    TextInput,
    View,
    Widget,
    do_not_read_this_widget,
)
from widgetastic.xpath import quote
from widgetastic_patternfly import (
    AggregateStatusCard,
    Button,
    FlashMessage,
    FlashMessages,
    Kebab,
    VerticalNavigation,
)
from widgetastic_patternfly4 import Pagination as PF4Pagination
from widgetastic_patternfly4.ouia import (
    Button as OUIAButton,
)
from widgetastic_patternfly4.table import BaseExpandableTable, BasePatternflyTable
from widgetastic_patternfly5 import (
    Button as PF5Button,
    ExpandableSection as PF5ExpandableSection,
    FormSelect,
    Progress as PF5Progress,
)
from widgetastic_patternfly5.ouia import (
    BaseSelect as PF5BaseSelect,
    Button as PF5OUIAButton,
    Dropdown as PF5OUIADropdown,
    Menu as PF5Menu,
    OUIAGenericWidget,
)

from airgun.exceptions import DisabledWidgetError, ReadOnlyWidgetError
from airgun.utils import get_widget_by_name


class SatSelect(Select):
    """Represent basic select element except our custom implementation remove
    html tags from select option values
    """

    SELECTED_OPTIONS_TEXT = """
var result_arr = [];
var opt_elements = arguments[0].selectedOptions;
for(var i = 0; i < opt_elements.length; i++){
    value = opt_elements[i].innerHTML;
    parsed_value = value.replace(/<[^>]+>/gm, '');
    result_arr.push(parsed_value);
}
return result_arr;
"""


class CheckboxWithAlert(Checkbox):
    """Represent basic checkbox element, but able to handle alert message
    which can appear after you perform action for that widget
    """

    def fill(self, value):
        value = bool(value)
        current_value = self.selected
        if value == current_value:
            return False
        else:
            self.click(handle_alert=True)
            if self.selected != value:
                raise WidgetOperationFailed('Failed to set the checkbox to requested value.')
            return True


class RadioGroup(GenericLocatorWidget):
    """Classical radio buttons group widget

    Example html representation::

        <div class="form-group ">
            <label>Protocol *</label>
        <div class="col-md-4">
            <label class="radio-inline">
                <input type="radio" checked="checked" name="subnet[type]">IPv4
            </label>
            <label class="radio-inline">
                <input type="radio" name="subnet[type]">IPv6
            </label>

    Locator example::

        //div/label[input[@type='radio']][contains(., 'IPv4')]

    """

    LABELS = './/label[input[@type="radio"]]'
    BUTTON = './/input[@type="radio"]'

    @property
    def button_names(self):
        """Return all radio group labels"""
        return [self.browser.text(btn) for btn in self.browser.elements(self.LABELS)]

    def _get_parent_label(self, name):
        """Get radio group label for specific button"""
        try:
            return next(
                btn for btn in self.browser.elements(self.LABELS) if self.browser.text(btn) == name
            )
        except StopIteration as err:
            raise NoSuchElementException(f"RadioButton {name} is absent on page") from err

    @property
    def selected(self):
        """Return name of a button that is currently selected in the group"""
        for name in self.button_names:
            btn = self.browser.element(self.BUTTON, parent=self._get_parent_label(name))
            if btn.get_attribute('checked') is not None:
                return name
        raise ValueError(
            "Whether no radio button is selected or proper attribute "
            "should be added to framework"
        )

    def select(self, name):
        """Select specific radio button in the group"""
        if self.selected != name:
            self.browser.element(self.BUTTON, parent=self._get_parent_label(name)).click()
            return True
        return False

    def read(self):
        """Wrap method according to architecture"""
        return self.selected

    def fill(self, name):
        """Wrap method according to architecture"""
        return self.select(name)


class ToggleRadioGroup(RadioGroup):
    """Toggle buttons group widget when each button represented by radio
    element

    Example html representation::

        <div class="form-group ">
            <div>
                <label>Template *</label>
            <div class="btn-group">
                <label class="btn btn-default btn-sm active">
                   <input type="radio" name="options">Input
                </label>
                <label class="btn btn-default btn-sm">
                   <input type="radio" name="options">Diff
                </label>

    Locator example::

        //div[@class='btn-group']

    """

    @property
    def selected(self):
        """Return name of a button that is currently selected in the group"""
        for name in self.button_names:
            btn = self.browser.element(self._get_parent_label(name))
            if 'active' in btn.get_attribute('class'):
                return name
        raise ValueError(
            "Whether no radio button is selected or proper attribute "
            "should be added to framework"
        )

    def select(self, name):
        """Select specific radio button in the group"""
        if self.selected != name:
            self.browser.element(self._get_parent_label(name)).click()
            return True
        return False


class DateTime(Widget):
    """Collection of date picker and two inputs for hours and minutes

    Example html representation::

        <div name="syncPlanForm">
            <div ... label="Start Date">
                <label for="startDate" class="ng-binding">Start Date</label>
                <input type="text" uib-datepicker-popup="" id="startDate" ...>
                <span class="input-group-btn">
                    <button type="button" class="btn btn-default"...>
                        <i class="fa fa-calendar"></i>
            <div ...label="Start Time">
                <label for="" class="ng-binding">Start Time</label>
                    <div show-meridian="false" id="startTime" ...>
                        <table...>
        ...

    Locator example::

        We don't need to pass locator here as widget seems has one structure
        across all applications that use paternfly pattern
    """

    start_date = TextInput(id='startDate')
    hours = TextInput(locator=".//input[@ng-model='hours']")
    minutes = TextInput(locator=".//input[@ng-model='minutes']")

    def fill(self, values):
        """Fills the widget accordingly to provided values.

        :param values: dict with keys ``start_date`` and/or ``hours``,
            and/or ``minutes`` containing values that should be present in
            the fields
        """
        for name in ['start_date', 'hours', 'minutes']:
            value = values.get(name, None)
            if value:
                getattr(self, name).fill(value)

    def read(self):
        """Read current widget values and put them into the dict

        :param values: dict with key/value pairs for all widget fields
        """
        values = {}
        for name in ['start_date', 'hours', 'minutes']:
            values[name] = getattr(self, name).read()
        return values


class DatePickerInput(TextInput):
    """Input for date, which opens calendar on click.

    Example html representation::

        <input type="date" uib-datepicker-popup="" ng-model="rule.start_date"
         ng-model-options="{timezone: 'UTC'}" is-open="date.startOpen"
         ng-click="openStartDate($event)">
            <div uib-datepicker-popup-wrap="" ng-model="date"
             ng-change="dateSelection(date)"
             template-url="uib/template/datepickerPopup/popup.html">
                <ul role="presentation" class="uib-datepicker-popup ..."
                 ng-if="isOpen" ng-keydown="keydown($event)"
                 ng-click="$event.stopPropagation()">
                ...
            </div>
            <span class="input-group-btn">
                    <button class="btn btn-default" type="button"
                     ng-click="openStartDate($event)">
                        <i class="fa fa-calendar inline-icon"></i>
                </button>
            </span>

    Locator example::

        ".//input[@ng-model='rule.start_date']"
    """

    CALENDAR_POPUP = "./parent::div/div[@ng-model='date']/ul[contains(@class, 'datepicker-popup')]"
    calendar_button = Text("./parent::div//button[i[contains(@class, 'fa-calendar')]]")
    clear_button = Text(f"{CALENDAR_POPUP}//button[@ng-click='select(null, $event)']")
    done_button = Text(f"{CALENDAR_POPUP}//button[@ng-click='close($event)']")

    @property
    def is_open(self):
        """Bool value whether the calendar is opened or not"""
        return (
            self.browser.wait_for_element(
                self.CALENDAR_POPUP, parent=self, timeout=1, exception=False
            )
            is not None
        )

    def clear(self):
        """Clear input value. Opens calendar popup if it's closed and pushes
        'Clear' button.
        """
        if not self.is_open:
            self.calendar_button.click()
        self.clear_button.click()

    def close_calendar(self):
        """Closes calendar popup if it's opened."""
        if self.is_open:
            self.done_button.click()

    def fill(self, value):
        """Custom fill which uses custom :meth:`clear` and closes calendar
        popup after filling.
        """
        current_value = self.value
        if value == current_value:
            return False
        self.browser.click(self)
        self.clear()
        self.browser.send_keys(value, self)
        self.close_calendar()
        return True


class ItemsList(GenericLocatorWidget):
    """List with click-able elements. Part of :class:`MultiSelect` or jQuery
    drop-down.

    Example html representation::

        <ul class="ms-list" tabindex="-1">

    Locator example::

        //ul[@class='ms-list']

    """

    ITEM = "./li[not(contains(@style, 'display: none'))][normalize-space(.)='{}']"
    ITEMS = "./li[not(contains(@style, 'display: none'))]"

    def read(self):
        """Return a list of strings representing elements in the
        :class:`ItemsList`."""
        return [el.text for el in self.browser.elements(self.ITEMS, parent=self)]

    def fill(self, value):
        """Clicks on element inside the list.

        :param value: string with element name
        """
        self.browser.click(self.browser.element(self.ITEM.format(value), parent=self))


class AddRemoveItemsList(GenericLocatorWidget):
    """Similar to ItemsList widget except list elements can be selected only using 'Add'
    and 'Remove' buttons near each of it

    Example html representation::

        <ul class="config_group_group">
            <li id="config_group_1" class="config_group ">
                <span>
                    <a onclick="expandClassList...">
                </span>
                <a onclick="addConfigGroup(this)">Add</a>
            </li>
        </ul>

    Locator example::

        //ul[@id='selected_config_groups']

    """

    ITEM_BUTTON = "./li[not(contains(@style, 'display: none'))][contains(., '{}')]/a"
    ITEMS = "./li[not(contains(@style, 'display: none'))]/span/a"

    def read(self):
        """Return a list of strings representing elements in the
        :class:`AddRemoveItemsList`."""
        return [el.text for el in self.browser.elements(self.ITEMS, parent=self)]

    def fill(self, value):
        """Clicks on whether Add or Remove button for necessary element from the list.

        :param value: string with element name
        """
        self.browser.click(self.browser.element(self.ITEM_BUTTON.format(value), parent=self))


class ItemsListGroup(GenericLocatorWidget):
    """Similar to ItemsList widget ideology, but here we have group of items lists instead.
    Each item list element from such group is placed inside expandable section

    Example html representation::

        <ul class="puppetclass_group">
            <li>
                <a onclick="expandClassList...">
                    stdlib
                </a>
                <ul id="pc_stdlib">
                    <li class="puppetclass">
                        <span>
                            <a...>stdlib</a>
                        </span>

                    </li>
                    <li class="puppetclass ">
                        <span>
                            <a...>stdlib::stages</a>
                        </span>
                </li>
            </li>
        </ul>

    Locator example::

        //div[contains(@class, 'available_classes')]/div[@class='row']

    """

    ITEM = (
        "./div/ul/li/ul/li[not(contains(@style, 'display: none'))]"
        "[normalize-space(.)='{}']/span/a"
    )
    ITEMS = "./div/ul/li/ul/li[not(contains(@style, 'display: none'))]"
    EXPAND = (
        "./div/ul/li/ul/li[not(contains(@style, 'display: none'))]"
        "[normalize-space(.)='{}']/../preceding-sibling::a"
    )

    def read(self):
        return [el.text for el in self.browser.elements(self.ITEMS, parent=self)]

    def fill(self, value):
        if not self.browser.is_displayed(self.ITEM.format(value)):
            self.browser.element(self.EXPAND.format(value), parent=self).click()
        self.browser.element(self.ITEM.format(value), parent=self).click()


class ItemsListReadOnly(ItemsList):
    def fill(self, value):
        raise ReadOnlyWidgetError('Widget is read only, fill is prohibited')


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

    filter = TextInput(locator=".//input[contains(@class,'ms-filter')]")
    unassigned = ItemsList("./div[@class='ms-selectable']/ul")
    assigned = ItemsList("./div[@class='ms-selection']/ul")

    add_all_button = Text(locator='.//a[contains(@class,"ms-select-all")]')
    remove_all_button = Text(locator='.//a[contains(@class,"ms-deselect-all")]')

    def __init__(self, parent, locator=None, id=None, logger=None):
        """Supports initialization via ``locator=`` or ``id=``"""
        if (locator and id) or (not locator and not id):
            raise TypeError('Please specify either locator or id')
        locator = locator or f".//div[@id='{id}']"
        super().__init__(parent, locator, logger)

    def fill(self, values):
        """Read current values, find the difference between current and passed
        ones and fills the widget accordingly.

        :param values: dict with keys ``assigned`` and/or ``unassigned``,
            containing list of strings, representing item names
        """
        current = self.read()
        to_add = [res for res in values.get('assigned', ()) if res not in current['assigned']]
        to_remove = [
            res for res in values.get('unassigned', ()) if res not in current['unassigned']
        ]
        if not to_add and not to_remove:
            return False
        if to_add:
            for value in to_add:
                if self.filter:
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

    def add_all(self):
        """Function adds all from left item select."""
        self.add_all_button.click()

    def remove_all(self):
        """Function removes all from right item select."""
        self.remove_all_button.click()


class MultiSelectNoFilter(MultiSelect):
    """This widget facilitates the movement of items between the unassigned and assigned lists. After providing values,
    they will be stored in a list. Unassigned items contains the list which compare with the values,
    if value is present it will assign the value or vise-versa."""

    more_item = Text('//span[@class="pf-v5-c-menu-toggle__toggle-icon"]')
    select_pages = Text('//ul[@class="pf-v5-c-menu__list"]/li[6]/button')
    available_role_template = '//div[@class="available-roles-container col-sm-6"]/div[2]/div'
    assigned_role_template = '//div[@class="assigned-roles-container col-sm-6"]/div[2]/div'

    def fill(self, values):
        """This method facilitates assigning value(s) both during creation and after creation.
        Compare this value list with the actual list of items present in the UI.
        If the lists match, assign the items.
        """
        self.more_item.click()
        self.select_pages.click()
        available_list = self.browser.elements(self.available_role_template)
        for data in available_list[1:]:
            if data.text.split(". ")[1] in values:
                data.click()
        return True

    def unassigned_values(self, values):
        """This method facilitates the removal of items from the assigned list, effectively unassigned them."""
        assigned_list = self.browser.elements(self.assigned_role_template)
        for data in assigned_list:
            if data.text.split(". ")[1] in values.values():
                data.click()
        return True

    def read_assigned_values(self, values):
        """Returns a list of assigned value(s)."""
        assigned_list = self.browser.elements(self.assigned_role_template)
        value = [
            data.text.split(". ")[1] for data in assigned_list if data.text.split(". ")[1] in values
        ]
        return value


class PF4MultiSelect(GenericLocatorWidget):
    """Typical two-pane multiselect widget. Allows to move items from
    list of ``unassigned`` entities to list of ``assigned`` ones and vice
    versa. PF4 version.
    """

    unassigned = ItemsList(".//ul[@aria-labelledby='permission-duel-select-available-pane-status']")
    assigned = ItemsList(".//ul[@aria-labelledby='permission-duel-select-chosen-pane-status']")
    move_to_assigned = Text(".//button[@aria-label='Add selected']")
    move_to_unassigned = Text(".//button[@aria-label='Remove selected']")

    def __init__(self, parent, locator=None, id=None, logger=None):
        """Supports initialization via ``locator=`` or ``id=``"""
        if (locator and id) or (not locator and not id):
            raise TypeError('Please specify either locator or id')
        locator = locator or f".//div[@id='{id}']"
        super().__init__(parent, locator, logger)

    def fill(self, values):
        """Read current values, find the difference between current and passed
        ones and fills the widget accordingly.

        :param values: dict with keys ``assigned`` and/or ``unassigned``,
            containing list of strings, representing item names
        """
        current = self.read()
        to_add = [res for res in values.get('assigned', ()) if res not in current['assigned']]
        to_remove = [
            res for res in values.get('unassigned', ()) if res not in current['unassigned']
        ]
        if not to_add and not to_remove:
            return False
        if to_add:
            for value in to_add:
                self.unassigned.fill(value)
                self.move_to_assigned.click()
        if to_remove:
            for value in to_remove:
                self.assigned.fill(value)
                self.move_to_unassigned.click()
        return True

    def read(self):
        """Returns a dict with current lists values."""
        unassigned = self.unassigned.read() if self.unassigned.is_displayed else []
        assigned = self.assigned.read() if self.assigned.is_displayed else []
        return {
            'unassigned': unassigned,
            'assigned': assigned,
        }


class PuppetClassesMultiSelect(MultiSelect):
    """Widget has different appearance than MultiSelect, because there are no actual panes,
    but logically it is the same. It looks like two lists of items and specific for puppet
    classes functionality. Allows to move items from list of 'available' entities to list
    of 'included' ones and vice versa. Named these lists as 'assigned' and 'unassigned'
    for proper inheritance.

    Examples on UI::
        Hosts -> Create Host -> Puppet Classes
        Configure -> Config Groups

    Example html representation::


        <div class="row">
            <div>
                <h3>Included Classes</h3>
                <ul id="selected_classes">
                </ul>
            </div>

            <div>
                 <h3>Available Classes</h3>
                 <ul class="puppetclass_group">
                 </ul>
            </div>
        </div>

    Locator examples::
        Usually it is empty locator, because it is impossible to build relative path

    """

    filter = TextInput(locator=".//input[@placeholder='Filter classes']")
    assigned = ItemsList(".//ul[@id='selected_classes']")
    unassigned = ItemsListGroup(".//div[contains(@class, 'available_classes')]/div[@class='row']")


class ConfigGroupMultiSelect(MultiSelect):
    """Similar to the PuppetClassesMultiSelect widget except items lists has different
    appearance and there is no filter field for available classes. Usually specific for config
    group functionality.
    """

    filter = None
    assigned = AddRemoveItemsList(".//ul[@id='selected_config_groups']")
    unassigned = AddRemoveItemsList(".//ul[@class='config_group_group']")


class ActionsDropdown(GenericLocatorWidget):
    """List of actions, expandable via button with caret. Usually comes with
    button attached on left side, representing either most common action or
    hint like 'Select Action'.

    Example html representation::

        <div class="btn-group dropdown" is-open="status.isOpen">
          <button type="button" class="btn btn-default" ...>
            <span><span >Select Action</span></span>
          </button>
          <button type="button" class="btn btn-default" ...>
            <span class="caret"></span>
          </button>
          <ul class="dropdown-menu dropdown-menu-right ng-scope" role="menu">
            <li role="menuitem"><a><span><span>Action1</span></span></a></li>
            <li role="menuitem"><a><span><span>Action2</span></span></a></li>
          </ul>
        </div>

    Locator example::

        //div[contains(@class, 'dropdown')]
        //div[contains(@class, 'btn-group')]

    """

    dropdown = Text(
        ".//*[self::a or self::button][contains(@class, 'dropdown-toggle') or "
        "contains(@ng-click, 'toggleDropdown')][contains(@class, 'btn')]"
        "[*[self::span or self::i][contains(@class, 'caret')]]"
    )
    pf4_drop_down = Text("//div[contains(@data-ouia-component-id, 'bookmarks-dropdown')]")
    button = Text(
        ".//*[self::button or self::span][contains(@class, 'btn') or "
        "contains(@aria-label, 'search button')]"
        "[not(*[self::span or self::i][contains(@class, 'caret')])]"
    )
    ITEMS_LOCATOR = './/ul/li/a'
    ITEM_LOCATOR = './/ul/li/a[normalize-space(.)="{}"]'

    @property
    def is_open(self):
        """Checks whether dropdown list is open."""
        try:
            return 'open' in self.browser.classes(
                self
            ) or 'pf-m-expanded' in self.pf4_drop_down.browser.classes(self.pf4_drop_down)
        except NoSuchElementException:
            return False

    def open(self):
        """Opens dropdown list"""
        if not self.is_open:
            try:
                self.dropdown.click()
            except NoSuchElementException:
                self.pf4_drop_down.click()

    def close(self):
        """Closes dropdown list"""
        if self.is_open:
            try:
                self.dropdown.click()
            except NoSuchElementException:
                self.pf4_drop_down.click()

    @property
    def items(self):
        """Returns a list of all dropdown items as strings."""
        self.open()
        items = [
            self.browser.text(el) for el in self.browser.elements(self.ITEMS_LOCATOR, parent=self)
        ]
        self.close()
        return items

    def select(self, item):
        """Selects item from dropdown."""
        if item in self.items:
            self.open()
            self.browser.element(self.ITEM_LOCATOR.format(item), parent=self).click()
        else:
            raise ValueError(
                f'Specified action "{item}" not found in actions list. '
                f'Available actions are {self.items}'
            )

    def fill(self, item):
        """Selects action. Apart from dropdown also checks attached button
        label if present"""
        if self.button.is_displayed and self.button.text == item:
            self.button.click()
        else:
            self.select(item)

    def read(self):
        """Returns a list of available actions."""
        return self.items


class Pf4ActionsDropdown(ActionsDropdown):
    """PF4 version of actions dropdown with support for items description

    Example html representation::

        <div class="pf-c-dropdown pf-m-expanded" data-ouia-component-type="PF4/Dropdown">
          <div class="pf-c-dropdown__toggle pf-m-split-button pf-m-action">
              <button class="pf-c-dropdown__toggle-button">Schedule a job</button>
              <button class="pf-c-dropdown__toggle-button pf-m-secondary">
              </button>
          </div>
          <ul class="pf-c-dropdown__menu" role="menu">
              <li "role="menuitem"><a><div>Run Puppet Once</div></a></li>
              <li "role="menuitem"><a><div>Run OpenSCAP scan</div></a></li>
              <li "role="menuitem"><a><div>Run Ansible roles</div></a></li>
              <li "role="menuitem"><a><div>Enable web console</div></a></li>
          </ul>
        </div>

    """

    button = Text(
        './/button[contains(@class,"pf-v5-c-dropdown__toggle-button")'
        'and not(@data-ouia-component-type="PF5/DropdownToggle")]'
    )
    dropdown = Text(
        './/button[contains(@class,"pf-v5-c-dropdown__toggle-button")'
        'and @data-ouia-component-type="PF5/DropdownToggle"]'
    )
    ITEMS_LOCATOR = ".//ul[contains(@class, 'pf-v5-c-dropdown__menu')]/li"
    ITEM_LOCATOR = ".//ul/li[@role='menuitem' and contains(normalize-space(.), '{}')]"

    @property
    def is_open(self):
        return 'pf-m-expanded' in self.browser.classes(self)

    @property
    def is_enabled(self):
        return 'pf-m-disabled' not in self.browser.classes(self)

    def select(self, item):
        self.open()
        self.browser.element(self.ITEM_LOCATOR.format(item), parent=self).click()


class ActionDropdownWithCheckbox(ActionsDropdown):
    """Custom drop down which contains the checkbox inside in drop down."""

    customize_check_box = Checkbox(id="customize")

    def fill(self, item):
        """select action from drop down list, after checking customize checkbox
        :param item: dictionary with values for 'is_customize' and 'action' keys.
        """
        self.open()
        self.customize_check_box.fill(item['is_customize'])
        self.select(item['action'])


class Search(Widget):
    """Searchbar for table filtering"""

    ROOT = (
        './/div[contains(@class, "toolbar-pf-filter") or contains(@class, "title_filter")'
        'or contains(@class, "dataTables_filter") or @id="search-bar"]'
    )
    search_field = TextInput(
        locator=(
            ".//input[@id='search' or contains(@placeholder, 'Filter') or "
            "@ng-model='table.searchTerm' or contains(@ng-model, 'Filter') or "
            "@data-autocomplete-id='searchBar' or contains(@placeholder, 'Search') "
            "or contains(@class, 'search-input') or contains(@aria-label, 'Search input')]"
        )
    )
    search_button = PF5Button(locator=(".//button[@aria-label='Search']"))
    clear_button = Text(
        ".//span[contains(@class,'autocomplete-clear-button') or contains(@class,'fa-close')]"
    )
    actions = ActionsDropdown(
        ".//*[self::div or self::span][contains(@class, 'input-group-btn') "
        "or contains(@class, 'pf-c-input-group')]"
    )

    def fill(self, value):
        return self.search_field.fill(value)

    def read(self):
        return self.search_field.read()

    def clear(self):
        """Clears search field value and re-trigger search to remove all
        filters.
        """
        if self.clear_button.is_displayed:
            self.clear_button.click()
        else:
            self.browser.clear(self.search_field)
        if self.search_button.is_displayed:
            self.search_button.click()

    def search(self, value):
        if hasattr(self.parent, 'flash'):
            # large flash messages may hide the search button
            self.parent.flash.dismiss()
        self.clear()
        self.fill(value)
        if self.search_button.is_displayed:
            self.search_button.click()


class PF4Search(Search):
    """PF4 Searchbar for table filtering"""

    ROOT = '//div[@class="foreman-search-bar"]'
    search_field = TextInput(locator=(".//input[@aria-label='Search input']"))
    search_button = Text(locator=(".//button[@aria-label='Search']"))
    clear_button = Text(locator=(".//button[@aria-label='Reset search']"))

    actions = ActionsDropdown("//div[contains(@data-ouia-component-id, 'bookmarks-dropdown')]")

    def clear(self):
        """Clears search field value and re-trigger search to remove all
        filters.
        """
        if self.clear_button.is_displayed:
            self.clear_button.click()
        else:
            self.browser.clear(self.search_field)

    def search(self, value):
        self.clear()
        self.fill(value)
        if self.search_button.is_displayed:
            self.search_button.click()


class PF5NavSearchMenu(PF5Menu, OUIAGenericWidget):
    """PF5 vertical navigation dropdown menu with search results."""

    @property
    def items(self):
        """Return list of :py:class:`WebElement` items in the menu."""
        return self.browser.elements(self.ITEMS_LOCATOR)

    def read(self):
        """Return all items in the menu as strings."""
        return [self.browser.text(el) for el in self.items]


class PF5NavSearch(PF4Search):
    """PF5 vertical navigation menu search."""

    ROOT = '//div[@id="navigation-search"]'
    search_field = TextInput(locator=".//input[@aria-label='Search input']")
    search_button = PF5Button(locator=".//button[@aria-label='Search']")
    clear_button = PF5Button(locator=".//button[@aria-label='Reset']")
    items = PF5NavSearchMenu(component_id="navigation-search-menu")
    results_timeout = search_clear_timeout = 2

    def _wait_for_results(self, results_widget):
        """Read the search results widget `results_widget` for `self.results_timeout` seconds
        and return the values. If timeout is exceeded, empty list is returned.

        :return: list[str] if values are returned; empty list otherwise
        """
        return (
            wait_for(
                lambda: results_widget.read(),
                timeout=self.results_timeout,
                delay=0.5,
                handle_exception=NoSuchElementException,
                silent_failure=True,
            )[0]
            or []
        )

    def _safe_search_clear(self):
        """Clear the search input and return if it is actually cleared."""
        if self.browser.text(self.search_field) != '':
            self.clear()
        return self.browser.text(self.search_field) == ''

    def _ensure_search_is_cleared(self):
        """Wait for `search_clear_timeout` seconds that the search input has been really cleared."""
        wait_for(
            lambda: self._safe_search_clear(),
            timeout=self.search_clear_timeout,
            delay=0.5,
        )

    def search(self, value):
        """Search the vertical navigation menu.
        Clear the input field afterward, so it does not interfere with the regular navigation menu.

        :param str value: search query
        :return: list of search results as strings
        """
        super().search(value)
        results = self._wait_for_results(results_widget=self.items)
        self._ensure_search_is_cleared()
        return results


class SatVerticalNavigation(VerticalNavigation):
    """The Patternfly Vertical navigation."""

    CURRENTLY_SELECTED = './/li[contains(@class, "active")]/a/span'


class SatFlashMessage(FlashMessage):
    """Satellite version of Patternfly alert. It doesn't contain ``<strong>``
    tag and all the text is inside 2 ``<span>``.

    For more details, see `Bugzilla #1566565
    <https://bugzilla.redhat.com/show_bug.cgi?id=1566565>`_.

    Should not be used directly, only via class:`SatFlashMessages`.

    Example html representation::

        <div class="alert toast-pf alert-success alert-dismissable">
                <button ... type="button" class="close close-default">
                    <span ... class="pficon pficon-close"></span></button>
                <span aria-hidden="true" class="pficon pficon-ok"></span>
                <span><span>Sample message</span></span></div>
        </div>

    """

    TYPE_MAPPING = {
        "pf-m-warning": "warning",
        "pf-m-success": "success",
        "pf-m-danger": "error",
        "pf-m-info": "info",
    }

    ROOT = ParametrizedLocator('.//div[contains(@class, "foreman-toast") and position()={index}]')
    TITLE_LOCATOR = './/h4[contains(@class, "alert__title")]'
    DISMISS_LOCATOR = './/div[contains(@class, "alert__action")]'
    ICON_LOCATOR = './/div[contains(@class, "alert__icon")]'
    DESCRIPTION_LOCATOR = './/div[contains(@class, "alert__description")]'

    @property
    def text(self):
        """Return the message text of the notification."""
        try:
            return self.browser.text(self.DESCRIPTION_LOCATOR)
        except NoSuchElementException:
            return self.browser.text(self.TITLE_LOCATOR)


class SatFlashMessages(FlashMessages):
    """Satellite version of Patternfly's alerts section. The only difference is
    overridden ``messages`` property which returns :class:`SatFlashMessage`.

    Example html representation::

        <ul class="pf-v5-c-alert-group pf-m-toast"><li>
        <div class="pf-v5-c-alert pf-m-success foreman-toast" aria-label="Success Alert"
            data-ouia-component-type="PF4/Alert" data-ouia-safe="true"
            data-ouia-component-id="OUIA-Generated-Alert-success-1">
            <div class="pf-c-alert__icon">

    Locator example::

        //ul[@class=pf-v5-c-alert-group pf-m-toast"]/li/div[contains(@class, pf-v5-c-alert")]

    """

    ROOT = '//ul[@class="pf-v5-c-alert-group pf-m-toast"]'
    MSG_LOCATOR = f'{ROOT}//div[contains(@class, "foreman-toast")]'
    msg_class = SatFlashMessage


class ValidationErrors(Widget):
    """Widget for tracking all improperly filled inputs inside view, which are
    highlighted with red color and typically contain error message next to
    them.

    Example html representation::

        <div class="form-group has-error">
            <label class="..." for="name">DNS Domain *</label>
            <div class="col-md-4">
                <input ... type="text" name="domain[name]" id="domain_name">
                <span class="help-block"></span>
            </div>
            <span class="help-block help-inline">
                <span class="error-message">can't be blank</span>
            </span>
        </div>

    Locator example::

        No locator accepted as widget should look through entire view.

    """

    ERROR_ELEMENTS = ".//*[(contains(@class,'has-error') or (contains(@class, 'pf-m-error') and string-length(normalize-space(string())) > 0)) and not(contains(@style,'display:none'))]"
    ERROR_MESSAGES = (
        ".//*[(contains(@class, 'alert base in fade alert-danger') "
        "or contains(@class, 'alert base in fade alert-warning') "
        "or contains(@class,'error-msg') "
        "or contains(@class,'error-msg-block') "
        "or contains(@class,'error-message') "
        "or contains(@class,'editable-error-block') "
        "or contains(@class,'pf-v5-c-helper-text__item-text')) "
        "and not(contains(@style,'display:none'))]"
    )

    @property
    def has_errors(self):
        """Returns boolean value whether view has fields with invalid data or
        not.
        """
        time.sleep(
            1
        )  # ensure_page_safe doesn't help here and there's nothing to wait_for because the error won't always be there
        return self.browser.elements(self.ERROR_ELEMENTS) != []

    @property
    def messages(self):
        """Returns a list of all validation messages for improperly filled
        fields. Example: ["can't be blank"]
        """
        error_msgs = self.browser.elements(self.ERROR_MESSAGES)
        if len(error_msgs) > 0:
            wait_for(
                lambda: any(self.browser.text(error_msg) for error_msg in error_msgs),
                timeout=10,
                delay=1,
            )
        return [self.browser.text(error_msg) for error_msg in error_msgs]

    def assert_no_errors(self):
        """Assert current view has no validation messages, otherwise rise
        ``AssertionError``.
        """
        if self.has_errors:
            raise AssertionError(
                f"Validation errors present on page, displayed messages: {self.messages}"
            )

    def read(self, *args, **kwargs):
        do_not_read_this_widget()


class ContextSelector(Widget):
    CURRENT_ORG = '//div[@data-ouia-component-id="taxonomy-context-selector-organization"]'
    CURRENT_LOC = '//div[@data-ouia-component-id="taxonomy-context-selector-location"]'
    ORG_LOCATOR = '//div[@id="organization-dropdown"]//li[button[contains(.,{})]]'
    LOC_LOCATOR = '//div[@id="location-dropdown"]//li[button[contains(.,{})]]'

    def select_org(self, org_name):
        self.logger.info('Selecting Organization %r', org_name)

        # Click current org to view the list
        e = self.browser.element(self.CURRENT_ORG)
        self.browser.move_to_element(e)
        self.browser.click(e)

        # Select the new org from the list
        e = self.browser.element(self.ORG_LOCATOR.format(quote(org_name)))
        e.click()

        self.browser.plugin.ensure_page_safe()

    @property
    def current_org(self):
        return self.browser.text(self.CURRENT_ORG)

    def select_loc(self, loc_name):
        self.logger.info('Selecting Location %r', loc_name)

        # Click current location to view the list
        e = self.browser.element(self.CURRENT_LOC)
        self.browser.move_to_element(e)
        self.browser.click(e)

        # Select the new location from the list
        e = self.browser.element(self.LOC_LOCATOR.format(quote(loc_name)))
        e.click()

        self.browser.plugin.ensure_page_safe()

    @property
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
    """Drop-down element with filtering functionality

    Example html representation::

        <div class="select2-container form-control" id="s2id_subnet_boot_mode">

    Locator example::

        id=subnet_boot_mode
        id=s2id_subnet_ipam

    """

    selected_value = Text("./ancestor::div[1]//span/span[contains(@class, 'rendered')]")
    open_filter = Text("./ancestor::div[1]//span/span[contains(@class, 'arrow')]")
    clear_filter = Text("./a/abbr")
    filter_criteria = TextInput(
        locator="//span[@class='select2-search select2-search--dropdown']//input"
    )
    filter_content = ItemsList(
        "//span[not(contains(@style, 'display: none')) and @class='select2-results']/ul"
    )

    def __init__(self, parent, id=None, locator=None, logger=None):
        """Supports initialization via ``id=`` or ``locator=``"""
        if (locator and id) or (not locator and not id):
            raise ValueError('Please specify either locator or id')
        locator = locator or f".//select[contains(@id, '{id}')]"
        super().__init__(parent, locator, logger)

    def read(self):
        """Return drop-down selected item value and remove special character using unicode u00d7"""
        return self.browser.text(self.selected_value).replace('\u00d7', '').strip()

    def clear(self):
        """Clear currently selected value for drop-down"""
        self.clear_filter.click()

    def fill(self, value):
        """Select specific item from the drop-down

        :param value: string with item value
        """
        if value == '':
            self.clear()
            return True
        self.open_filter.click()
        self.filter_criteria.fill(value)
        self.filter_content.fill(value)


class PF4FilteredDropdown(GenericLocatorWidget):
    """Drop-down element with filtering functionality - PatternFly 4 version"""

    filter_criteria = TextInput(locator=".//input[@aria-label='Select a resource type']")
    filter_content = ItemsList(".//ul")

    def clear(self):
        """Clear currently selected value for drop-down"""
        self.browser.clear(self.filter_criteria)

    def fill(self, value):
        """Select specific item from the drop-down

        :param value: string with item value
        """
        self.clear()
        self.filter_criteria.fill(value)
        self.filter_content.fill(value)

    def read(self):
        """Return drop-down selected item value"""
        return self.browser.text(self.filter_criteria)


class CustomParameter(Table):
    """Name-Value paired input elements which can be added, edited or removed.

    It is essentially a table with text input widgets on each row, with an
    "Add New Parameter" button on the same page.

    Example html representation::

        <table class="table" id="global_parameters_table">
            <tr class="fields " id="new_os_parameter_row">
                <input placeholder="Name" type="text" ... id="..._name">
                <textarea id="new_os_parameter_value" placeholder="Value" ...>

    Locator example::

        //input[@placeholder='Name']
        //textarea[@placeholder='Value']

    """

    add_new_value = Text("..//a[contains(normalize-space(.),'+ Add Parameter')]")

    def __init__(self, parent, **kwargs):
        """Supports initialization via ``locator=`` or ``id=``"""
        if (kwargs.get('locator') and kwargs.get('id')) or (
            not kwargs.get('locator') and not kwargs.get('id')
        ):
            raise ValueError('Please specify either locator or id')
        locator = kwargs.get('locator') or f".//table[@id='{kwargs.pop('id')}']"
        kwargs.update({'locator': f'{locator}'})

        # Implementation of parameters is inconsistent as to whether a new row
        # is added to the top or bottom of the table when adding a parameter.
        # Views representing pages that add new parameters to the bottom of the
        # table can pass a `new_row_bottom = True` kwarg to the CustomParameter
        # __init__ method.
        if kwargs.get('new_row_bottom'):
            self.new_row_bottom = kwargs.pop('new_row_bottom')
        else:
            self.new_row_bottom = False
        super().__init__(parent, **kwargs)

        self.column_widgets = kwargs.get('column_widgets') or {
            'Name': TextInput(locator=".//input[@placeholder='Name']"),
            'Value': TextInput(locator=".//textarea[@placeholder='Value']"),
            'Actions': Text(
                locator=".//a[@data-original-title='Remove Parameter' "
                "or @title='Remove Parameter']"
            ),
        }
        self.name = next(iter(self.column_widgets.keys()))
        self.name_key = '_'.join(self.name.lower().split(' '))
        self.value = list(self.column_widgets.keys())[1]
        self.value_key = '_'.join(self.value.lower().split(' '))

    def read(self):
        """Return a list of dictionaries. Each dictionary consists of name and
        value parameters
        """
        parameters = []
        for row in self.rows():
            name = row[self.name].widget.read()
            value = row[self.value].widget.read()
            parameters.append({self.name_key: name, self.value_key: value})
        return parameters

    def add(self, value):
        """Add single name/value parameter entry to the table.

        :param value: dict with format {'name': str, 'value': str}
        """
        self.add_new_value.click()
        if self.new_row_bottom:
            new_row = self.__getitem__(-1)
        else:
            new_row = self.__getitem__(0)
        new_row.wait_displayed()
        new_row[self.name].widget.fill(value[self.name_key])
        new_row[self.value].widget.fill(value[self.value_key])

    def remove(self, name):
        """Remove parameter entries from the table based on name.

        :param value: dict with format {'name': str, 'value': str}
        """
        for row in self.rows():
            if row[self.name].widget.read() == name:
                row['Actions'].widget.click()  # click 'Remove'

    def fill(self, values):
        """Fill parameter entries. Existing values will be overwritten.

        Updates name/value pairs if the name is already in the list.

        If you desire to intentionally add a duplicate value, use self.add()

        :param values: either single dictionary of name and value, or list
            of name/value dictionaries
        """
        if isinstance(values, dict):
            params_to_fill = [values]
        else:
            params_to_fill = values

        try:
            names_to_fill = [param[self.name_key] for param in params_to_fill]
        except KeyError as err:
            raise KeyError("parameter value is missing 'name' key") from err
        # Check if duplicate names were passed in and skip incase list
        if names_to_fill and not isinstance(names_to_fill[0], dict):
            if len(set(names_to_fill)) < len(names_to_fill):
                raise ValueError(
                    "Cannot use fill() with duplicate parameter names. "
                    "If you wish to explicitly add a duplicate name, "
                    "use CustomParameter.add()"
                )

        # Check if we need to update or remove any rows
        for row in self.rows():
            this_name = row[self.name].widget.read()
            this_value = row[self.value].widget.read()
            if this_name not in names_to_fill:
                # Delete row if its name/value is not in desired values
                row['Actions'].widget.click()  # click 'Remove' icon
            else:
                # Check if value should be updated for this name
                # First get the desired value for this param name
                desired_value = None
                for index, param in enumerate(params_to_fill):
                    if param[self.name_key] == this_name:
                        desired_value = param[self.value_key]
                        # Since we're editing this name now, don't add it later
                        params_to_fill.pop(index)
                        break
                if desired_value is not None and this_value != desired_value:
                    # Update row's value for this name
                    row[self.value].widget.fill(desired_value)
                else:
                    # Desired parameter name/value is already filled
                    continue

        # Add the remaining values for names that were not already in the table
        for param in params_to_fill:
            self.add(param)


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
    cancel_dialog = Text(".//button[contains(@ng-click, 'cancel') and contains(@class, 'btn')]")
    discard_dialog = Text(".//button[contains(@ng-click, 'cancel') and @class='close']")

    def _check_is_displayed(self, elem):
        """This is to check if dialog is displayed"""
        wait_for(lambda: elem.is_displayed, timeout=10, delay=1, logger=self.logger)

    def confirm(self):
        """Clicks on the positive outcome button like 'Remove', 'Ok', 'Yes'"""
        self._check_is_displayed(self.confirm_dialog)
        self.confirm_dialog.click()

    def cancel(self):
        """Clicks on the negative outcome button like 'Cancel' or 'No'"""
        self._check_is_displayed(self.cancel_dialog)
        self.cancel_dialog.click()

    def read(self):
        """Widgets has no fields to read"""
        do_not_read_this_widget()


class Pf4ConfirmationDialog(ConfirmationDialog):
    """PF4 confirmation dialog with two buttons and close 'x' button in the
    right corner."""

    ROOT = '//div[@id="app-confirm-modal" or @data-ouia-component-type="PF4/ModalContent"]'
    confirm_dialog = OUIAButton('btn-modal-confirm')
    cancel_dialog = OUIAButton('btn-modal-cancel')
    discard_dialog = OUIAButton('app-confirm-modal-ModalBoxCloseButton')


class Pf5ConfirmationDialog(ConfirmationDialog):
    """PF5 confirmation dialog with two buttons and close 'x' button in the
    right corner."""

    ROOT = '//div[@id="app-confirm-modal" or @data-ouia-component-type="PF5/ModalContent"]'
    confirm_dialog = PF5OUIAButton('btn-modal-confirm')
    cancel_dialog = PF5OUIAButton('btn-modal-cancel')
    discard_dialog = PF5OUIAButton('app-confirm-modal-ModalBoxCloseButton')


class LCESelector(GenericLocatorWidget):
    """Group of checkboxes that goes in a line one after another. Usually used
    to specify lifecycle environment

    Example html representation::

        <ul[@class='path-list']>
            <li class="path-list-item ng-scope"...>
                <label class="path-list-item-label...>
                    <input type="checkbox"...>
            <li class="path-list-item ng-scope"...>
                <label class="path-list-item-label...>
                    <input type="checkbox"...>

    Locator example::

        //ul[@class='path-list']

    """

    ROOT = ParametrizedLocator("{@locator}")
    LABELS = "./li/label[contains(@class, path-list-item-label)]"
    CHECKBOX = './/input[@ng-model="item.selected"][parent::label[contains(., "{}")]]'

    def __init__(self, parent, locator=None, logger=None):
        """Allow to specify ``locator`` if needed or use default one otherwise.
        Locator is needed when multiple :class:`LCESelector` are present,
        typically as a part of :class:`airgun.views.common.LCESelectorGroup`.
        """
        if locator is None:
            locator = ".//div[contains(@class, 'path-selector')]//ul[@class='path-list']"
        super().__init__(parent, locator, logger=logger)

    def checkbox_selected(self, locator):
        """Identify whether specific checkbox is selected or not"""
        return 'ng-not-empty' in self.browser.get_attribute('class', locator, parent=self)

    def select(self, locator, value):
        """Select or deselect checkbox depends on the value passed"""
        value = bool(value)
        current_value = self.checkbox_selected(locator)
        if value == current_value:
            return False
        self.browser.click(locator, parent=self)
        if self.checkbox_selected(locator) != value:
            raise WidgetOperationFailed('Failed to set the checkbox to requested value.')
        return True

    def read(self):
        """Return a dictionary where keys are lifecycle environment names and
        values are booleans whether they're selected or not.
        """
        checkboxes = {}
        for item in self.browser.elements(self.LABELS, parent=self):
            name = self.browser.text(item, parent=self)
            value = self.checkbox_selected(self.CHECKBOX.format(name))
            checkboxes[name] = value
        return checkboxes

    def fill(self, value):
        """Assign value for specific checkbox from group

        :param value: dictionary that consist of single checkbox name and
            value that should be assigned to that checkbox
        """
        checkbox_name = next(iter(value.keys()))
        checkbox_value = value[checkbox_name]
        checkbox_locator = self.CHECKBOX.format(checkbox_name)
        return self.select(checkbox_locator, checkbox_value)


class PF5LCESelector(LCESelector):
    """Group of checkboxes that goes in a line one after another. Usually used
    to specify lifecycle environment, updated for PF5 pages
    """

    LABELS = './/label[contains(@class, "pf-v5-c-radio__label")]'
    CHECKBOX = './/input[contains(@class, "pf-v5-c-radio__input") and ../label[.//*[contains(text(), "{}")]]]'

    def __init__(self, parent, locator=None, logger=None):
        """Allow to specify ``locator`` if needed or use default one otherwise.
        Locator is needed when multiple :class:`LCESelector` are present,
        typically as a part of :class:`airgun.views.common.LCESelectorGroup`.
        """
        if locator is None:
            locator = './/div[contains(@class, "env-path")]'
        super().__init__(parent, locator, logger=logger)

    def checkbox_selected(self, locator):
        """Identify whether specific checkbox is selected or not"""
        return self.browser.is_selected(locator)


class PF5LCECheckSelector(PF5LCESelector):
    """Checkbox version of PF5 LCE Selector"""

    LABELS = './/label[contains(@class, "pf-v5-c-check__label")]'
    CHECKBOX = (
        './/input[contains(@class, "pf-v5-c-check") and ../label[.//*[contains(text(), "{}")]]]'
    )


class LimitInput(Widget):
    """Input for managing limits (e.g. Hosts limit). Consists of 'Unlimited'
    checkbox and text input for specifying the limit, which is only visible if
    checkbox is unchecked.

    Example html representation::

        <input type="checkbox" name="limit"
         ng-model="activationKey.unlimited_hosts"...>

        <input id="max_hosts" name="max_hosts"
         ng-model="activationKey.max_hosts"
         ng-required="!activationKey.unlimited_hosts" type="number" min="1"
         max="2147483648"...>

    Locator example::

        No locator accepted as widget consists of multiple other widgets in
        different parts of DOM. Please use View's ``ROOT`` for proper isolation
        if needed.

    """

    unlimited = Checkbox(
        locator=(
            ".//input[@type='checkbox'][contains(@ng-required, 'unlimited') "
            "or contains(@ng-model, 'unlimited')]"
        )
    )
    limit = TextInput(locator=(".//input[@type='number'][contains(@ng-required, 'unlimited')]"))

    def fill(self, value):
        """Handle 'Unlimited' checkbox before trying to fill text input.

        :param value: either 'Unlimited' (case insensitive) to select
            corresponding checkbox or value to fill text input with.
        """
        if self.read().lower() == str(value).lower():
            return False
        if str(value).lower() == 'unlimited':
            self.unlimited.fill(True)
        else:
            self.unlimited.fill(False)
            self.limit.fill(value)
        return True

    def read(self):
        """Return either 'Unlimited' if corresponding checkbox is selected
        or text input value otherwise.
        """
        if self.unlimited.read():
            return 'Unlimited'
        return self.limit.read()


class TextInputHidden(TextInput):
    """Text input widget with content that may be hidden"""

    def read(self):
        value = super().read()
        hidden = 'masked-input' in self.browser.classes(self)
        return {'value': value, 'hidden': hidden}


class EditableEntry(GenericLocatorWidget):
    """Usually represented by static field and edit button that transform
    field into control to change field content to specific value. That control
    can have different appearances like textarea, input, select and etc. That
    widget is specific for entity edit pages.

    Example html representation::

        <dl>
            <dt>
            <dd>
                <form>
                ...
                    <span class="fr" ng-hide="editMode || readonly"...>
                    <span class="editable-value ng-binding">

    Locator example::

        //dt[contains(., 'test')]/following-sibling::dd/span
        //dt[contains(., 'test')]/following-sibling::dd/input

    """

    edit_button = Text(".//span[contains(@ng-hide, 'editMode')]")
    edit_field = TextInput(locator=".//*[self::input or self::textarea]")
    save_button = Text(".//button[normalize-space(.)='Save']")
    cancel_button = Text(".//button[span[normalize-space(.)='Cancel']]")
    entry_value = Text(".//span[contains(@class, 'editable-value')]")
    pf4_edit_button = Text("//button[@aria-label='edit name']")
    pf4_edit_field = TextInput(locator=".//input[@aria-label='name text input']")
    pf4_save_button = Text("//button[@aria-label='submit name']")
    pf4_cancel_button = Text("//button[@aria-label='clear name']")

    def __init__(self, parent, locator=None, name=None, logger=None):
        """Supports initialization via ``locator=`` or ``name=``"""
        if (locator and name) or (not locator and not name):
            raise TypeError('Please specify either locator or name')
        locator = locator or f".//dt[normalize-space(.)='{name}']/following-sibling::dd[1]"
        super().__init__(parent, locator, logger)

    def fill(self, value):
        """Fill widget with necessary value

        :param value: string with value that should be used for field update
            procedure
        """
        # in some cases editing fields automatically triggers editing others,
        # so the field may be opened for editing and clicking "edit" button is
        # not required for it
        if self.edit_button.is_displayed:
            self.edit_button.click()
        if self.edit_field.is_displayed:
            self.edit_field.fill(value)
            self.save_button.click()
        if self.pf4_edit_button.is_displayed:
            self.pf4_edit_button.click()
        if self.pf4_edit_field.is_displayed:
            self.pf4_edit_field.fill(value)
            self.pf4_save_button.click()

    def read(self):
        """Returns string with current widget value"""
        return self.entry_value.read()


class EditableEntrySelect(EditableEntry):
    """Should be used in case :class:`EditableEntry` widget represented not by
    a field, but by select list.
    """

    edit_field = Select(locator=".//select")


class EditableEntryCheckbox(EditableEntry):
    """Should be used in case :class:`EditableEntry` widget represented not by
    a field, but by checkbox.
    """

    edit_field = Checkbox(locator=".//input[@type='checkbox']")


class CheckboxGroup(GenericLocatorWidget):
    """
    A set of checkboxes of the same property type
    """

    ITEMS_LOCATOR = './/p'
    CHECKBOX_LOCATOR = './/p[normalize-space(.)="{}"]/input'

    @cached_property
    def checkboxes(self):
        labels = [line.text for line in self.browser.elements(self.ITEMS_LOCATOR, parent=self)]
        return {
            label: Checkbox(self, locator=self.CHECKBOX_LOCATOR.format(label)) for label in labels
        }

    def read(self):
        """Read values of checkboxes"""
        return {name: checkbox.read() for name, checkbox in self.checkboxes.items()}

    def fill(self, values):
        """Check or uncheck one of the checkboxes

        :param value: string with specification of fields' values
            Example: value={'details.role': {'Test role 1': True, 'Test role 2': False}}
        """
        for name, value in values.items():
            self.checkboxes[name].fill(value)


class EditableEntryMultiCheckbox(EditableEntry):
    """Should be used in case :class:`EditableEntry` widget represented not by
    a field, but by a set of checkboxes.
    """

    edit_field = CheckboxGroup(locator='.//form')


class TextInputsGroup(GenericLocatorWidget):
    """
    A set of text inputs
    """

    FIELD_LABELS = './/div[contains(@id,"template-input-")]//label'
    TEXTINPUT_LOCATOR = (
        './/div[contains(@id,"template-input-")]//'
        'label[normalize-space(.)="{}"]/following-sibling::div//input'
    )

    @cached_property
    def labels(self):
        return [line.text for line in self.browser.elements(self.FIELD_LABELS, parent=self)]

    @cached_property
    def textinputs(self):
        return {
            label: TextInput(self, locator=self.TEXTINPUT_LOCATOR.format(label))
            for label in self.labels
        }

    def read(self):
        """Read values of text inputs"""
        return {name: textinput.read() for name, textinput in self.textinputs.items()}

    def fill(self, values):
        """Fill one of the text inputs

        :param value: string with specification of fields' values
            Example: value={'Hosts filter': 'name=host11.example.com',
            'Errata filter': 'whatever'}
        """
        for name, value in values.items():
            self.textinputs[name].fill(value)


class EditableLimitEntry(EditableEntry):
    """Should be used in case :class:`EditableEntry` widget represented not by
    a field, but by :class:`LimitInput` widget."""

    edit_field = LimitInput()


class EditableDateTime(EditableEntry):
    """Should be used in case :class:`EditableEntry` widget represented not by
    a field, but by :class:`DateTime` widget."""

    edit_field = DateTime()


class ReadOnlyEntry(GenericLocatorWidget):
    """Similar to EditableEntry and specific for the same page types, but cannot
    be modified.

    Example html representation::

        <dl>
            <dt>
            <dd>
                <form>
                ...
                    <span class="ng-scope">No</span>

    Locator example::

        //dt[contains(., 'test')]/following-sibling::dd
        //dt[contains(., 'test')]/following-sibling::dd/span


    """

    entry_value = Text(".")
    BASE_LOCATOR = (
        ".//dt[contains(., '{}')]/following-sibling::dd[not(contains(@class, 'ng-hide'))][1]"
    )

    def __init__(self, parent, locator=None, name=None, logger=None):
        """Supports initialization via ``locator=`` or ``name=``"""
        if (locator and name) or (not locator and not name):
            raise TypeError('Please specify either locator or name')
        locator = locator or self.BASE_LOCATOR.format(name)
        super().__init__(parent, locator, logger)

    def read(self):
        """Returns string with current widget value"""
        return self.entry_value.read().strip()


class ACEEditor(Widget):
    """Default ace editor

    Example html representation::

        <div id="editor-000" class="editor ace_editor ace-twilight ace_dark">
            <textarea class="ace_text-input"
            <div class="ace_gutter" style="display: none;">
                <div class="ace_layer ace_gutter-layer ace_folding-enabled">
            <div class="ace_scroller">
            <div class="ace_content">
                ...

    Locator example::

        There is no need to provide any locators to that widget

    """

    ROOT = "//div[contains(@class, 'ace_editor')]"

    def __init__(self, parent, logger=None):
        """Getting id for specific ace editor element"""
        Widget.__init__(self, parent, logger=logger)
        self.ace_edit_id = self.browser.element(self.ROOT).get_attribute("id")

    def fill(self, value):
        """Fill widget with necessary value

        :param value: string with value that should be used for field update
            procedure
        """
        self.browser.execute_script(f"ace.edit('{self.ace_edit_id}').setValue(arguments[0])", value)

    def read(self):
        """Returns string with current widget value"""
        return self.browser.execute_script(f"return ace.edit('{self.ace_edit_id}').getValue();")


class Pagination(Widget):
    """Represents Paginator widget that includes per page selector, First/Last/Next/Prev buttons
    and current page index/overall amount of pages. Mainly used with Table widget.
    """

    ROOT = ".//foreman-react-component[contains(@name, 'Pagination')]"
    # Kattelo views use per_page with select, foreman use a per_page with Button DropDown.
    PER_PAGE_BUTTON_DROPDOWN = ".//div[button[@id='paginationoptions-menu-toggle-3']]"
    PER_PAGE_SELECT = ".//select[contains(@ng-model, 'per_page')]"
    first_page_button = Button(".//div[button[@data-action='first']]")
    previous_page_button = Button(".//div[button[@data-action='previous']]")
    next_page_button = Button(".//div[button[@data-action='next']]")
    last_page_button = Button(".//div[button[@data-action='last']]")
    page = TextInput(locator=".//input[contains(@class, 'pf-c-form-control')]")
    pages = Text("//div[contains(@class, 'pf-c-pagination__nav-page-select')]//span")
    total_items = Text(".//span[contains(@class, 'pf-c-options-menu__toggle-text')]/b[2]")

    @cached_property
    def per_page(self):
        """Return the per page widget"""
        if (
            self.browser.wait_for_element(
                self.PER_PAGE_SELECT, parent=self, timeout=1, exception=False
            )
            is not None
        ):
            return Select(self, self.PER_PAGE_SELECT)
        return ActionsDropdown(self, self.PER_PAGE_BUTTON_DROPDOWN)

    @property
    def is_displayed(self):
        """Check whether this Pagination widget exists and visible"""
        return (
            self.browser.wait_for_element(
                self.pages, parent=self, visible=True, timeout=1, exception=False
            )
            is not None
        )

    def _click_button(self, pager_button):
        """Click on the pager button if enabled."""
        if "disabled" not in self.browser.classes(pager_button):
            pager_button.click()
        else:
            raise DisabledWidgetError(f'Button {pager_button} is not enabled')

    def first_page(self):
        """Goto first page by clicking on first page button"""
        self._click_button(self.first_page_button)

    def previous_page(self):
        """Goto previous page by clicking on previous page button"""
        self._click_button(self.previous_page_button)

    def next_page(self):
        """Goto next page by clicking on next page button"""
        self._click_button(self.next_page_button)

    def last_page(self):
        """Goto last page by clicking on last page button"""
        self._click_button(self.last_page_button)

    @property
    def current_page(self):
        """Return the current page as integer value"""
        return int(self.page.read())

    @property
    def total_pages(self):
        """Return the total available pages as integer value"""
        return int(self.pages.read())

    def read(self):
        """Read the basic sub widgets of this pagination widget"""
        return {
            attr: getattr(self, attr).read()
            for attr in ('per_page', 'page', 'pages', 'total_items')
        }

    def fill(self, values):
        """Fill sub widgets with the supplied values"""
        if not values:
            values = {}
        for key, value in values.items():
            widget = get_widget_by_name(self, key)
            if widget:
                widget.fill(value)


class SatTable(Table):
    """Satellite version of table.

    Includes a paginator sub-widget. If found, then the paginator is used to read all entries from
    the table.

    If the table is empty, there might be only one column with an appropriate message in the table
    body, or it may have no columns or rows at all. This subclass handles both possibilities.

    It also ignores all hidden columns, which some tables might contain, like the Hosts table.

    Example html representation::

        <table bst-table="table" ...>
           <thead>
             <tr class="ng-scope">
               <th class="row-select"><input type="checkbox" ...></th>
               <th ng-click="table.sortBy(column)" ...>
                <span ...><span ...>Column Name</span></span><i ...></i></th>
               <th ng-click="table.sortBy(column)" ...>
                <span ...><span ...>Column Name</span></span><i ...></i></th>
             </tr>
           </thead>
           <tbody>
            <tr id="noRowsTr"><td colspan="9">
                 <span data-block="no-rows-message" ...>
                    <span class="ng-scope">Table is empty</span></span>
            </td></tr>
           </tbody>
         </table>

    Locator example::

        .//table

    """

    HEADER_IN_ROWS = "./tbody/tr[1]/th[not(@hidden)]"
    HEADERS = (
        "./thead/tr/th[not(@hidden)]|./tr/th[not(@hidden)]|./thead/tr/td[not(@hidden)]"
        + "|"
        + HEADER_IN_ROWS
    )
    COLUMN_AT_POSITION = "./td[not(@hidden)][{0}]"

    no_rows_message = (
        ".//td/span[contains(@data-block, 'no-rows-message') or "
        "contains(@data-block, 'no-search-results-message')]"
    )
    tbody_row = Text('./tbody/tr')
    pagination = PF4Pagination(
        locator="//div[contains(@class, 'pf-c-pagination') and not(contains(@class, 'pf-m-compact'))]"
    )

    @property
    def has_rows(self):
        """Boolean value whether table contains some elements (rows) or is
        empty.
        """
        try:
            no_rows = self.browser.element(self.no_rows_message)
        except NoSuchElementException:
            no_rows = False
        if no_rows or not self.tbody_row.is_displayed:
            return False
        return True

    def read_limited(self, limit):
        """This is almost the same as inherited read but has a limit. Use it for tables that take too long to read.
        Reads the table. Returns a list, every item in the list is contents read from the row."""
        rows = list(self)
        # Cut the unwanted rows if necessary
        if self.rows_ignore_top is not None:
            rows = rows[self.rows_ignore_top :]
        if self.rows_ignore_bottom is not None and self.rows_ignore_bottom > 0:
            rows = rows[: -self.rows_ignore_bottom]
        if self.assoc_column_position is None:
            ret = []
            rows_read = 0
            for row in rows:
                if rows_read >= limit:
                    break
                ret.append(row.read())
                rows_read = rows_read + 1
            return ret
        else:
            result = {}
            rows_read = 0
            for row in rows:
                if rows_read >= limit:
                    break
                row_read = row.read()
                try:
                    key = row_read.pop(self.header_index_mapping[self.assoc_column_position])
                except KeyError:
                    try:
                        key = row_read.pop(self.assoc_column_position)
                    except KeyError:
                        try:
                            key = row_read.pop(self.assoc_column)
                        except KeyError as e:
                            raise ValueError(
                                f"The assoc_column={self.assoc_column!r} could not be retrieved"
                            ) from e
                if key in result:
                    raise ValueError(f"Duplicate value for {key}={result[key]!r}")
                result[key] = row_read
                rows_read = rows_read + 1
            return result

    def read(self, limit=None):
        """Return empty list in case table is empty"""
        if not self.has_rows:
            self.logger.debug(f'Table {self.locator} is empty')
            return []
        if limit is not None:
            return self.read_limited(limit)
        if self.pagination.is_displayed:
            return self._read_all()
        return super().read()

    def _read_all(self):
        """Return all available table values with using pagination navigation."""
        table_rows = []
        page_number = 1
        if self.pagination.current_page != page_number:
            # goto first page
            self.pagination.first_page()
            wait_for(
                lambda: self.pagination.current_page == page_number,
                timeout=30,
                delay=1,
                logger=self.logger,
            )
        while page_number <= self.pagination.total_pages:
            page_table_rows = super().read()
            table_rows.extend(page_table_rows)
            if page_number == self.pagination.total_pages:
                break
            self.pagination.next_page()
            page_number += 1
            # ensure that we are at the right page (to not read the same page twice) and
            # to escape any ui bug that will cause hanging on this loop.
            wait_for(
                lambda page_number=page_number: self.pagination.current_page == page_number,
                timeout=30,
                delay=1,
                logger=self.logger,
            )
        return table_rows


class SatSubscriptionsTable(SatTable):
    """Subscriptions table, which has extra preceding row for 'Repository Name'
    column. It's equal to satellite table in all other respects.

    Example::

        Following table cells:

        TestSubscriptionName
        1|0 out of Unlimited|Physical|Start_Date|End_Date|Support_Level
        TestSubscriptionName2
        1|0 out of Unlimited|Physical|Start_Date|End_Date|Support_Level

        Will be transformed into:

        TestSubscriptionName|1|0 out of Unlimited|Physical|Start_Date|...
        TestSubscriptionName2|1|0 out of Unlimited|Physical|Start_Date|...

        So, title rows will be removed in favor of extra column 'Repository
        Name'.

    Example html representation::

        <table bst-table="table" ...>
         ...
         <tbody>
            <!-- ngRepeat: (name, subscriptions) in groupedSubscriptions -->
            ...
         </tbody>
        </table>


    Locator example::

        .//table

    """

    title_rows = None  # container for 'Repository Name' rows

    def rows(self, *extra_filters, **filters):
        """Split list of all the rows into 'content' rows and 'title' rows.
        Return content rows only.
        """
        rows = super().rows(*extra_filters, **filters)
        if self.has_rows:
            rows = list(rows)
            self.title_rows = rows[0:][::2]
            return iter(rows[1:][::2])
        return rows

    def read(self):
        """Return content rows with 1 extra column 'Repository Name' in it."""
        read_rows = super().read()
        if self.has_rows:
            titles = iter(column[1].read() for column in self.title_rows)
            for row in read_rows:
                row['Repository Name'] = next(titles)
        return read_rows


class SatTableWithoutHeaders(Table):
    """Applicable for every table in application that has no headers. Due logic of the Table
    widget we have to explicitly specify custom headers. As we have no idea about the content
    and structure of the table in advance, we will dynamically name each column using simple -
    'column1', 'column2', ... 'columnN'.

    Example html representation::

        <table>
            <tbody>
                <tr>
                    <td>Name</td>
                    <td>my_host</td>
                    <td>my_new_host</td>
                </tr>
                <tr>
                    <td>Arhitecture</td>
                    <td>x32</td>
                    <td>x64</td>
                </tr>
            </tbody>
        </table>

    Locator example::

        //table[@id='audit_table']
    """

    ROWS = './tbody/tr'
    COLUMNS = './tbody/tr[1]/td'
    ROW_AT_INDEX = './tbody/tr[{0}]'
    # there is no header row elements in this table.
    HEADER_IN_ROWS = None
    HEADERS = None

    @property
    def _is_header_in_body(self):
        """Explicitly return False as there is no header row in this table."""
        return False

    @cached_property
    def headers(self):
        result = []
        for index, _ in enumerate(self.browser.elements(self.COLUMNS, parent=self)):
            result.append(f'column{index}')

        return tuple(result)


class SatTableWithUnevenStructure(SatTable):
    """Applicable for every table in application that has uneven amount of
    headers and columns(usually we talk about 1 header but 2 columns)
    We taking into account that all possible content rows are actually present
    in DOM, but some are 'hidden' using css class. Also we can specify what
    widget we expect in a second column (e.g. link or text)

    Some examples where we can use current class:
    'Content Counts' table present in every repository, containing amount of
    packages/source RPM's/Errata/etc with links to corresponding details pages.
    'Properties' table present in every host details page

    Example html representation::

        <table class="table table-striped table-bordered">
            <thead>
            <tr>
              <th colspan="2" ...>Content Type</th>
            </tr>
            </thead>

            <tbody>
            <tr ng-show="repository.content_type === 'yum'" class="ng-hide" style="">
              <!-- translate: --><td translate="" class="ng-scope" style="">Packages</td>
              <td class="align-center">
                <a ui-sref="product.repository.manage-content.packages(...)" class="ng-binding"
                  href=".../repositories/<repo-id>/content/packages">
                  0
                </a>
              </td>
            </tr>

            ...

            <tr ng-show="repository.content_type === 'docker'">
              <!-- translate: -->
                <td translate="" class="ng-scope" style="">Container Image Manifests</td>
              <td class="align-center">
                <a ui-sref="product.repository.manage-content.docker-manifests(...)"
                  class="ng-binding"
                  href=".../repositories/<repo-id>/content/content/docker_manifests">
                  0
                </a>
              </td>
            </tr>
            ...
            </tbody>
        </table>

    Locator example::

        .//table[//th[normalize-space(.)="Content Type"]]
        //table[@id='properties_table']


    """

    def __init__(self, parent, locator, column_locator='.', logger=None):
        """Defining locator to find a table on a page and widget that is going
        to be used to work with data in a second column
        """
        column_widgets = {1: Text(locator=column_locator)}
        super().__init__(parent, locator=locator, logger=logger, column_widgets=column_widgets)

    def read(self):
        """Returns a dict with {column1: column2} values, and only for rows
        which aren't marked as hidden.

        Example::

            {
                'Packages': '1',
                'Package Groups': '0'
                'Status': 'OK'
                'Domain': 'domain_name'
            }

        """
        return {
            row[0].read(): row[1].read()
            for row in self.rows()
            if 'ng-hide' not in self.browser.classes(row)
        }


class ProgressBar(GenericLocatorWidget):
    """Generic progress bar widget.

    Example html representation::

        <div class="progress ng-isolate-scope" type="success" ...>
          <div class="progress-bar progress-bar-success" aria-valuenow="0"
           aria-valuemin="0" aria-valuemax="100" aria-valuetext="0%" ...></div>
        </div>

    Locator example::

        .//div[contains(@class, "progress progress-striped")]

    """

    PROGRESSBAR = './/div[contains(@class,"progress-bar")]'

    def __init__(self, parent, locator=None, logger=None):
        """Provide common progress bar locator if it wasn't specified."""
        Widget.__init__(self, parent, logger=logger)
        if not locator:
            locator = './/div[contains(@class, "progress progress-striped")]'
        self.locator = locator

    @property
    def is_active(self):
        """Boolean value whether progress bar is active or not (stopped,
        pending or any other state).
        """
        if 'active' in self.browser.classes(self, check_safe=False):
            return True
        return False

    @property
    def progress(self):
        """String value with current flow rate in percent."""
        return self.browser.get_attribute('aria-valuetext', self.PROGRESSBAR, check_safe=False)

    @property
    def is_completed(self):
        """Boolean value whether progress bar is finished or not"""
        if not self.is_active and self.progress == '100%':
            return True
        return False

    def wait_for_result(self, timeout=600, delay=1):
        """Waits for progress bar to finish. By default checks whether progress
        bar is completed every second for 10 minutes.

        :param timeout: integer value for timeout in seconds
        :param delay: float value for delay between attempts in seconds
        """
        wait_for(lambda: self.is_displayed, timeout=30, delay=delay, logger=self.logger)
        wait_for(
            lambda: not self.is_displayed or self.is_completed is True,
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )

    def read(self):
        """Returns current progress."""
        return self.progress


class PF5ProgressBar(PF5Progress):
    ROOT = './/div[contains(@class, "pf-v5-c-wizard__main-body")]'

    def __init__(self, parent, locator=None, logger=None):
        """Overrides `locator` parameter to be optional with default of `PF5ProgressBar.ROOT`"""
        self.locator = locator or self.ROOT
        super().__init__(parent, self.locator, logger=logger)

    @property
    def is_displayed(self):
        if progress_bar := self.browser.wait_for_element(
            self.PROGRESS_BAR, timeout=1, exception=False
        ):
            return progress_bar.is_displayed
        return False

    @property
    def is_completed(self):
        """Boolean value whether progress bar is finished or not"""
        try:
            return self.current_progress == '100'
        except NoSuchElementException:
            return False

    def wait_for_result(self, timeout=600, delay=1):
        """Waits for progress bar to finish. By default checks whether progress
        bar is completed every second for 10 minutes.
        :param timeout: integer value for timeout in seconds
        :param delay: float value for delay between attempts in seconds
        """
        wait_for(lambda: self.is_displayed, timeout=30, delay=delay, logger=self.logger)
        wait_for(
            lambda: not self.is_displayed or self.is_completed,
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )


class PublishPromoteProgressBar(ProgressBar):
    """Progress bar for Publish and Promote procedures. They contain status
    message and link to associated task. Also the progress is displayed
    slightly differently.

    Example html representation::

        <a ng-href="/foreman_tasks/tasks/71196" ng-hide="hideProgress(version)"
         href="/foreman_tasks/tasks/...71196">

          <div ng-class="{ active: taskInProgress(version) }"
           class="progress progress-striped">
            <div class="progress ng-isolate-scope" animate="false" ...>
            <div class="progress-bar" aria-valuenow="" aria-valuemin="0"
             aria-valuemax="100" aria-valuetext="%" ...></div></div>
          </div>
          Publishing and promoting to 1 environment.
        </a>
        <span ng-show="hideProgress(version)" ...>
          Published
          (2018-05-07 18:10:14 +0300)
        </span>

    Locator example::

        .//div[contains(@class, "progress progress-striped")]

    """

    ROOT = '.'
    TASK = Text('.//a[contains(@ng-href, "/foreman_tasks/")]')
    MESSAGE = Text('.//span[@ng-show="hideProgress(version)"]')

    @property
    def is_completed(self):
        """Boolean value whether progress bar is finished or not"""
        # Value is empty before and after publish, the only way to figure out
        # whether progress completed or not even started - to check result
        # message presence
        # Promoting finishes with `100%`
        if self.MESSAGE.is_displayed and self.progress in ('100%', '%'):
            return True
        return False

    def read(self):
        """Returns message with either progress or result, depending on its
        status.
        """
        if self.is_completed:
            return self.MESSAGE.read()
        return self.TASK.read()


class PieChart(GenericLocatorWidget):
    """Default Pie Chart that can be found across application. At that moment
    only return values that displayed inside of the chart
    """

    chart_title_text = Text(
        ".//*[name()='svg']//*[name()='tspan'][contains(@class,'donut-title-small-pf')]"
    )
    chart_title_value = Text(
        ".//*[name()='svg']//*[name()='tspan'][contains(@class,'donut-title-big-pf')]"
    )

    def read(self):
        """Return dictionary that contains chart title name as key and chart
        value as its value
        """
        return {self.chart_title_text.read(): self.chart_title_value.read()}


class RemovableWidgetsItemsListView(View):
    """A host for widgets list. Items that can be added or removed, mainly used in profile for
    network interfaces, storage and job template.

    Usage::

        @View.nested
        class resources(RemovableWidgetsItemsListView):
            ROOT = "//fieldset[@id='storage_volumes']"
            ITEMS = "./div/div[contains(@class, 'removable-item')]"
            ITEM_WIDGET_CLASS = ComputeResourceRHVProfileStorageItem
    """

    ITEMS = "./div[contains(@class, 'removable-item')]"
    ITEM_WIDGET_CLASS = None
    ITEM_REMOVE_BUTTON_ATTR = 'remove_button'
    add_item_button = Text(".//a[contains(@class, 'add_nested_fields')]")

    def _get_item_locator(self, index):
        """Return the item locator located at index position"""
        return f'{self.ITEMS}[{index + 1}]'

    def get_item_at_index(self, index):
        """Return the item widget instance at index"""
        return self.ITEM_WIDGET_CLASS(self, self._get_item_locator(index))

    def add_item(self):
        """Add an item by pressing the add_item button and return the item instance"""
        self.add_item_button.click()
        return self.get_item_at_index(self.items_length - 1)

    def remove_item(self, item):
        """Remove item widget by clicking on it's remove button"""
        if self.ITEM_REMOVE_BUTTON_ATTR:
            getattr(item, self.ITEM_REMOVE_BUTTON_ATTR).click()

    def remove_item_at_index(self, index):
        """Remove item at index"""
        self.remove_item(self.get_item_at_index(index))

    @property
    def items_length(self):
        # Returns the items length
        return len(self.browser.elements(self.ITEMS, parent=self))

    @property
    def items(self):
        """Return all the items widget instances"""
        return [self.get_item_at_index(index) for index in range(self.items_length)]

    def clear(self):
        """Remove all items if item remove button attribute defined."""
        if self.ITEM_REMOVE_BUTTON_ATTR:
            for item in reversed(self.items):
                self.remove_item(item)

    def read(self):
        """Read all items"""
        return [item.read() for item in self.items]

    def fill(self, values):
        """Fill all items.
        :param values: A list of values to fill the item widgets with.
        """
        if not values:
            values = []
        # Clear all before fill
        self.clear()
        for value in values:
            item = self.add_item()
            item.fill(value)


class GenericRemovableWidgetItem(GenericLocatorWidget):
    """Generic Item widget (to be inherited) and to be used as Widget Item for
    `RemovableWidgetsItemsListView`.
    """

    remove_button = Text(".//div[@class='remove-button']/a")

    # Context is needed to support ConditionalSwitchableView in derived classes
    context = {}

    def read(self):
        values = {}
        for widget_name in self.widget_names:
            widget = getattr(self, widget_name)
            try:
                value = widget.read()
            except NoSuchElementException:
                continue
            values[widget_name] = value
        return values

    def fill(self, values):
        if values:
            for key, value in values.items():
                # in case of nested Views and ConditionalSwitchableView the key can be like "a.b.c"
                widget = get_widget_by_name(self, key)
                if widget:
                    widget.fill(value)


class AutoCompleteTextInput(TextInput):
    """Autocomplete Search input field, We must remove the focus from this widget after fill to
    force the auto-completion list to be hidden. Since this is a react component, calling browser
    clear method directly on the field has no effect, thus we need to clear the field using the
    clear button attached to the input
    """

    clear_button = Text(
        locator="//span[contains(@class,'autocomplete-clear-button') or "
        "contains(@class,'fa-close')]"
    )

    def clear(self):
        """Clears search field value and re-trigger search to remove all
        filters.
        """
        if self.clear_button.is_displayed:
            self.clear_button.click()
        else:
            self.browser.clear(self)

    def fill(self, value):
        old_value = self.value
        self.clear()
        super().fill(value)
        self.browser.plugin.ensure_page_safe()
        self.browser.send_keys_to_focused_element('\t')
        return self.value != old_value


class ToggleButton(Button):
    """A simple toggle button that we can read/write it's state via the standard view functions
    read/fill
    """

    def __init__(self, parent, *text, locator=None, **kwargs):
        self.locator = locator
        super().__init__(parent, *text, **kwargs)

    def __locator__(self):
        if self.locator:
            return self.locator
        return super().__locator__()

    def fill(self, value):
        value = bool(value)
        current_value = self.active
        if value != current_value:
            self.click()
            return True
        return False

    def read(self):
        return self.active


class Link(Text):
    """A link representation that we can read/click via the standard view functions read/fill."""

    def fill(self, value):
        if value:
            self.browser.click(self)


class PopOverModalView(View):
    """Popover-content UI widget which contains header, drop_down, input_box, or textarea and
    submit button. This is associated within a table.

    Example html representation::

        <div class="modal-content" role="document">
            <h4 class="modal-title">Update value for Connect by IP setting</h4>
            <form class="form-horizontal well">
                <select name="value" class="form-control">
                    <option value="true">Yes</option>
                    <option value="false">No</option>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">

        <div class="modal-content" role="document">
            <h4 class="modal-title">Update value for Administrator email address setting</h4>
            <form class="form-horizontal well">
                <input name="value" class="form-control" value="root@rhts.example.com">
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">

    Locator example::

        //div[contains(@class,'modal-content')]
    """

    ROOT = "//div[contains(@class,'modal-content')]"
    header = Text(".//h4[contains(@class, 'modal-title')]")
    input_box = TextInput(locator=".//input[contains(@class, 'form-control')]")
    textarea = TextInput(locator=".//textarea[contains(@class, 'form-control')]")
    drop_down = Select(".//select[contains(@class,'form-control')]")
    submit = Text(".//button[@type='submit']")


class PopOverWidget(View):
    """Popover-content UI widget which contains header, drop_down, input_box, or textarea and
    submit button. This is associated within a table.

    Locator example::

        //div[contains(@class, 'editable-open')]
    """

    ROOT = '.'
    column_value = Text(
        './/div[contains(@class, "ellipsis-pf-tooltip editable") '
        'or contains(@class,"ellipsis editable") '
        'or contains(@class,"ellipsis editable-empty editable")]'
    )
    pop_over_view = PopOverModalView()

    def fill(self, item):
        """Selects value from drop_down if exist otherwise write into input_box or textarea"""
        self.column_value.click()
        if self.pop_over_view.header.is_displayed:
            for widget_name in ('input_box', 'textarea', 'drop_down'):
                widget = getattr(self.pop_over_view, widget_name)
                if widget.is_displayed:
                    widget.fill(item)
                    break
        else:
            raise ReadOnlyWidgetError('This field setting is read-only')
        self.pop_over_view.submit.click()

    def read(self):
        """read column updated value"""
        return self.column_value.read()


class FieldWithEditButton(Widget):
    """A pair of a field and a button that makes the field editable.
    After editing, confirm by checkmark or cancel by X.
    Is present e.g. in PF5 Settings.
    """

    ROOT = '//td[2]'
    text_input = TextInput(locator=".//input[@data-ouia-component-type='PF5/TextInput']")
    text_area = TextInput(locator=".//textarea")
    drop_down = FormSelect(locator=".//select[@data-ouia-component-type='PF5/FormSelect']")
    edit_button = PF5Button(locator=".//button[contains(@data-ouia-component-id, 'edit-row')]")
    confirm_button = PF5OUIAButton('submit-edit-btn')
    cancel_button = PF5OUIAButton('cancel-edit-btn')
    text = Text(locator=".//span")

    def fill(self, item):
        self.edit_button.click()
        for widget_name in ['text_input', 'text_area', 'drop_down']:
            widget = getattr(self, widget_name)
            if widget.is_displayed:
                widget.fill(item)
                break
        self.confirm_button.click()

    def read(self):
        return self.text.read()


class AuthSourceAggregateCard(AggregateStatusCard):
    """This is a customizable card widget which has the title, count and kebab widget

    Example html representation::

        <div class="card-pf-body">
            <div class="dropdown pull-right dropdown-kebab-pf">
                <ul class="dropdown-menu dropdown-menu-right" aria-labelledby="dropupKebabRight2">
                    <li><a href="/auth_source_externals/3/edit">Edit</a></li>
                </ul>
            </div>
            <h2 class="card-pf-title text-center">
                    External
            </h2>
            <div class="card-pf-items text-center">
                <div class="card-pf-item">
                    <span class="pficon pficon-users"></span>
                    <span class="card-pf-item-text"><a href="">10</a></span>
                </div>
            </div>
        </div>
    """

    ROOT = ParametrizedLocator('.//h2[contains(normalize-space(.), {@name|quote})]/parent::div')
    select_kebab = Kebab(locator="./div[contains(@class, 'dropdown-kebab-pf')]")
    COUNT = ".//span[@class='card-pf-item-text']"

    @property
    def count(self):
        """Count of sources.

        :return int or None: None if no count element is found, otherwise count of sources in the card.
        """
        try:
            return int(self.browser.text(self.browser.element(self.COUNT)))
        except NoSuchElementException:
            return None


class Accordion(View, ClickableMixin):
    """PF4 Accordion widget"""

    ROOT = ParametrizedLocator("{@locator}")
    ITEMS = ".//button[contains(@class, 'pf-c-accordion__toggle')]"
    ITEM = ".//span[contains(normalize-space(.), '{}')]"

    def __init__(self, parent=None, id=None, locator=None, logger=None):
        Widget.__init__(self, parent=parent, logger=logger)
        self.locator = './/div[@id={id!r}]' if id else locator

    def items(self):
        return [self.browser.text(elm) for elm in self.browser.elements(self.ITEMS)]

    def toggle(self, value):
        self.browser.click(self.ITEM.format(value))


class BaseMultiSelect(PF5BaseSelect, PF5OUIADropdown):
    """Represents the Patternfly Multi Select.

    https://www.patternfly.org/v4/documentation/react/components/select#multiple
    """

    BUTTON_LOCATOR = './/button[@aria-label="Options menu"]'
    OUIA_COMPONENT_TYPE = "PF5/Select"
    SELECTED_ITEMS_LIST = './/div[@class="pf-v5-c-chip-group"]'

    def item_select(self, items, close=True):
        """Opens the Dropdown and selects the desired items.

        Args:
            items: Items to be selected
            close: Close the dropdown when finished
        """
        if not isinstance(items, list | tuple | set):
            items = [items]
        if isinstance(items, str):
            items = items.split(',')
        try:
            for item in items:
                element = self.item_element(item, close=False)
                if not element.find_element("xpath", "./..").get_attribute('aria-selected'):
                    element.click()
        finally:
            self.browser.click(self.BUTTON_LOCATOR)

    def fill(self, items):
        """Fills all the items.

        Args:
            items: list containing what items to be selected
        """
        try:
            self.item_select(items, close=False)
        finally:
            self.close()

    def read(self):
        try:
            return self.browser.text(self.SELECTED_ITEMS_LIST).split(' ')
        except NoSuchElementException:
            return None


class InventoryBootstrapSwitch(Widget):
    """Checkbox-like Switch control, representing On and Off state. But with
    fancy UI and without any <form> elements.
    There's also BootstrapSwitch widget in widgetastic_patternfly, but we don't
    inherit from it as it uses completely different HTML structure than this one
    (it has underlying <input>).
    """

    ON_TOGGLE = ".//span[contains(@class, 'bootstrap-switch-handle-on')]"
    OFF_TOGGLE = ".//span[contains(@class, 'bootstrap-switch-handle-off')]"
    ROOT = ParametrizedLocator("//div[@class={@class_name|quote}]/div")

    def __init__(self, parent, class_name, **kwargs):
        Widget.__init__(self, parent, logger=kwargs.pop('logger', None))
        self.class_name = class_name

    @property
    def selected(self):
        return 'bootstrap-switch-on' in self.browser.classes(self)

    @property
    def _clickable_el(self):
        """In automation, you need to click on exact toggle element to trigger action

        Returns: selenium webelement
        """
        locator = self.ON_TOGGLE
        if not self.selected:
            locator = self.OFF_TOGGLE
        return self.browser.element(locator=locator)

    def fill(self, value):
        if bool(value) == self.selected:
            return False
        else:
            self.browser.click(self._clickable_el)
            return True

    def read(self):
        return self.selected


class SearchInput(TextInput):
    """Searchbar's contained input text, and buttons"""

    search_field = TextInput(locator=('//input[@aria-label="Search input"]'))
    clear_button = Text(locator=('//button[@aria-label="Reset search"]'))

    def clear(self):
        """Clear search input by clicking the clear_button.
        Return: True if button was present, and clicking it caused it to disappear.
        False otherwise.
        """
        changed = False
        if self.clear_button.is_displayed:
            self.clear_button.click()
            # after clicking clear button, it should disappear
            if not self.clear_button.is_displayed:
                changed = True
        return changed

    def fill(self, value, enter_timeout=1, after_enter_timeout=3):
        """Fill the search input with supplied value"""
        changed = super().fill(value)
        if changed:
            # workaround for BZ #2140636
            time.sleep(enter_timeout)
            self.browser.send_keys(Keys.ENTER, self)
            time.sleep(after_enter_timeout)
        return changed


class EditModal(View):
    """Class representing the Edit modal header"""

    title = Text('.//h1')
    close_button = OUIAButton('acs-edit-details-modal-ModalBoxCloseButton')

    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')


class DualListSelector(EditModal):
    """Class representing the Dual List Selector in a modal."""

    available_options_search = SearchInput(locator='.//input[@aria-label="Available search input"]')
    available_options_list = ItemsList(
        locator='.//ul[contains(@aria-labelledby, "selector-available-pane-status")]'
    )

    add_selected = PF5Button(locator='.//button[@aria-label="Add selected"]')
    add_all = PF5Button(locator='.//button[@aria-label="Add all"]')
    remove_all = PF5Button(locator='.//button[@aria-label="Remove all"]')
    remove_selected = PF5Button(locator='.//button[@aria-label="Remove selected"]')

    chosen_options_search = SearchInput(locator='.//input[@aria-label="Chosen search input"]')
    chosen_options_list = ItemsList(
        locator='.//div[contains(@class, "pf-m-chosen")]'
        '//ul[@class="pf-c-dual-list-selector__list"]'
    )


class SatPatternflyTable(BasePatternflyTable, Table):
    def __init__(
        self,
        parent,
        column_widgets=None,
        assoc_column=None,
        rows_ignore_top=None,
        rows_ignore_bottom=None,
        top_ignore_fill=False,
        bottom_ignore_fill=False,
        logger=None,
    ):
        self.component_type = "PF4/Table"
        super().__init__(
            parent,
            locator=(f".//*[@data-ouia-component-type={quote(self.component_type)}]"),
            column_widgets=column_widgets,
            assoc_column=assoc_column,
            rows_ignore_top=rows_ignore_top,
            rows_ignore_bottom=rows_ignore_bottom,
            top_ignore_fill=top_ignore_fill,
            bottom_ignore_fill=bottom_ignore_fill,
            logger=logger,
        )


class SatExpandableTable(BaseExpandableTable, SatPatternflyTable):
    pass


class PF5LabeledExpandableSection(PF5ExpandableSection):
    """PF5 Expandable section (https://pf5.patternfly.org/components/expandable-section/)
    with a labeled button as the section expand/collapse toggle.

    Note: You need to set the `label` attribute yourself in your inherited class!
    """

    ROOT = ParametrizedLocator(
        '//div[contains(@class, "-c-expandable-section")]/button[normalize-space(.)={@label|quote}]/..'
    )
    BUTTON_LOCATOR = ParametrizedLocator('.//button[normalize-space(.)={@label|quote}]')
    label = 'You need to set this `label` attribute yourself!'

    def read(self):
        self.expand()


class PF5DataList(Widget):
    """Widget for PatternFly 5 Data list: https://pf5.patternfly.org/components/data-list"""

    ROOT = './/ul[contains(@class, "-c-data-list")]'
    ITEMS = './li//div[contains(@class, "-c-data-list__item-content")]/div[1]'
    VALUES = './li//div[contains(@class, "-c-data-list__item-content")]/div[2]'

    def read(self):
        items = [self.browser.text(item) for item in self.browser.elements(self.ITEMS)]
        values = [self.browser.text(value) for value in self.browser.elements(self.VALUES)]
        if len(items) != len(values):
            raise ValueError(
                f'The count of data list labels and values does not match. Labels: {items}. Values: {values}'
            )
        return dict(zip(items, values))
