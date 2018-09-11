from jsmin import jsmin
from wait_for import wait_for
from widgetastic.exceptions import (
    NoSuchElementException, WidgetOperationFailed)


from widgetastic.widget import (
    Checkbox,
    do_not_read_this_widget,
    GenericLocatorWidget,
    ParametrizedLocator,
    Select,
    Table,
    Text,
    TextInput,
    Widget,
)
from widgetastic.xpath import quote
from widgetastic_patternfly import (
    FlashMessage,
    FlashMessages,
    VerticalNavigation,
)

from airgun.exceptions import ReadOnlyWidgetError


class SatSelect(Select):
    """Represent basic select element except our custom implementation remove
    html tags from select option values
    """
    SELECTED_OPTIONS_TEXT = jsmin('''\
            var result_arr = [];
            var opt_elements = arguments[0].selectedOptions;
            for(var i = 0; i < opt_elements.length; i++){
                value = opt_elements[i].innerHTML;
                parsed_value = value.replace(/<[^>]+>/gm, '');
                result_arr.push(parsed_value);
            }
            return result_arr;
        ''')


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
                raise WidgetOperationFailed(
                    'Failed to set the checkbox to requested value.')
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
        return [
            self.browser.text(btn)
            for btn
            in self.browser.elements(self.LABELS)
        ]

    def _get_parent_label(self, name):
        """Get radio group label for specific button"""
        try:
            return next(
                btn for btn in self.browser.elements(self.LABELS)
                if self.browser.text(btn) == name
            )
        except StopIteration:
            raise NoSuchElementException(
                "RadioButton {name} is absent on page".format(name=name))

    @property
    def selected(self):
        """Return name of a button that is currently selected in the group"""
        for name in self.button_names:
            btn = self.browser.element(
                self.BUTTON, parent=self._get_parent_label(name))
            if btn.get_attribute('checked') is not None:
                return name
        else:
            raise ValueError(
                "Whether no radio button is selected or proper attribute "
                "should be added to framework"
            )

    def select(self, name):
        """Select specific radio button in the group"""
        if self.selected != name:
            self.browser.element(
                self.BUTTON, parent=self._get_parent_label(name)).click()
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
        else:
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


class ItemsList(GenericLocatorWidget):
    """List with click-able elements. Part of :class:`MultiSelect` or jQuery
    drop-down.

    Example html representation::

        <ul class="ms-list" tabindex="-1">

    Locator example::

        //ul[@class='ms-list']

    """
    ITEM = ("./li[not(contains(@style, 'display: none'))]"
            "[normalize-space(.)='%s']")
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
        to_add = [
            res
            for res in values.get('assigned', ())
            if res not in current['assigned']
        ]
        to_remove = [
            res
            for res in values.get('unassigned', ())
            if res not in current['unassigned']
        ]
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
    search_field = TextInput(locator=(
        ".//input[@id='search' or @ng-model='table.searchTerm' or "
        "contains(@ng-model, 'Filter')]"))
    search_button = Text(
        ".//button[contains(@type,'submit') or "
        "@ng-click='table.search(table.searchTerm)']"
    )

    def fill(self, value):
        return self.search_field.fill(value)

    def read(self):
        return self.search_field.read()

    def clear(self):
        """Clears search field value and re-trigger search to remove all
        filters.
        """
        self.browser.clear(self.search_field)
        if self.search_button.is_displayed:
            self.search_button.click()

    def search(self, value):
        if hasattr(self.parent, 'flash'):
            # large flash messages may hide the search button
            self.parent.flash.dismiss()
        self.fill(value)
        if self.search_button.is_displayed:
            self.search_button.click()


class SatVerticalNavigation(VerticalNavigation):
    """The Patternfly Vertical navigation."""
    CURRENTLY_SELECTED = './/li[contains(@class, "active")]/a/span'


class SatFlashMessages(FlashMessages):
    """Satellite version of Patternfly's alerts section. The only difference is
    overridden ``messages`` property which returns :class:`SatFlashMessage`.

    Example html representation::

        <div class="toast-notifications-list-pf">
            <div class="alert toast-pf alert-success alert-dismissable">
                <button ... type="button" class="close close-default">
                    <span ... class="pficon pficon-close"></span></button>
                <span aria-hidden="true" class="pficon pficon-ok"></span>
                <span><span>Sample message</span></span></div>
            </div>
        </div>

    Locator example::

        //div[@class="toast-notifications-list-pf"]

    """

    @property
    def messages(self):
        result = []
        try:
            for flash_div in self.browser.elements(
                    './div[contains(@class, "alert")]', parent=self,
                    check_visibility=True):
                result.append(
                    SatFlashMessage(self, flash_div, logger=self.logger))
        except NoSuchElementException:
            pass
        return result


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

    @property
    def text(self):
        return self.browser.text('./span/span', parent=self)


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
    ERROR_ELEMENTS = (
        ".//*[contains(@class,'has-error') and "
        "not(contains(@style,'display:none'))]"
    )
    ERROR_MESSAGES = (
        ".//*[(contains(@class,'error-msg-block') "
        "or contains(@class,'error-message')) "
        "and not(contains(@style,'display:none'))]"
    )

    @property
    def has_errors(self):
        """Returns boolean value whether view has fields with invalid data or
        not.
        """
        return self.browser.elements(self.ERROR_ELEMENTS) != []

    @property
    def messages(self):
        """Returns a list of all validation messages for improperly filled
        fields. Example: ["can't be blank"]
        """
        error_msgs = self.browser.elements(self.ERROR_MESSAGES)
        return [
            self.browser.text(error_msg)
            for error_msg in error_msgs
        ]

    def assert_no_errors(self):
        """Assert current view has no validation messages, otherwise rise
        ``AssertionError``.
        """
        if self.has_errors:
            raise AssertionError(
                "Validation errors present on page, displayed messages: {}"
                .format(self.messages)
            )

    def read(self, *args, **kwargs):
        do_not_read_this_widget()


class ContextSelector(Widget):
    CURRENT_ORG = '//li[@id="organization-dropdown"]/a'
    CURRENT_LOC = '//li[@id="location-dropdown"]/a'
    ORG_LOCATOR = '//li[@id="organization-dropdown"]/ul/li/a[contains(.,{})]'
    LOC_LOCATOR = '//li[@id="location-dropdown"]/ul/li/a[contains(.,{})]'

    def select_org(self, org_name):
        self.logger.info('Selecting Organization %r' % org_name)
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
        self.logger.info('Selecting Location %r' % loc_name)
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
    """Drop-down element with filtering functionality

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

    def __init__(self, parent, id=None, locator=None, logger=None):
        """Supports initialization via ``id=`` or ``locator=``"""
        if locator and id or not locator and not id:
            raise ValueError('Please specify either locator or id')
        locator = locator or ".//div[contains(@id, '{}')]".format(id)
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
    add_new_value = Text("..//a[contains(text(),'+ Add Parameter')]")

    def __init__(self, parent, locator=None, id=None, logger=None):
        """Supports initialization via ``locator=`` or ``id=``"""
        if locator and id or not locator and not id:
            raise ValueError('Please specify either locator or id')
        locator = locator or ".//table[@id='{}']".format(id)

        column_widgets = {
            'Name': TextInput(locator=".//input[@placeholder='Name']"),
            'Value': TextInput(locator=".//textarea[@placeholder='Value']"),
            'Actions': Text(
                locator=".//a[@data-original-title='Remove Parameter']"
            )
        }
        super(CustomParameter, self).__init__(parent,
                                              locator=locator,
                                              logger=logger,
                                              column_widgets=column_widgets)

    def read(self):
        """Return a list of dictionaries. Each dictionary consists of name and
        value parameters
        """
        parameters = []
        for row in self.rows():
            name = row['Name'].widget.read()
            value = row['Value'].widget.read()
            parameters.append({'name': name, 'value': value})
        return parameters

    def add(self, value):
        """Add single name/value parameter entry to the table.

        :param value: dict with format {'name': str, 'value': str}
        """
        self.add_new_value.click()
        new_row = self.__getitem__(-1)
        new_row['Name'].widget.fill(value['name'])
        new_row['Value'].widget.fill(value['value'])

    def remove(self, name):
        """Remove parameter entries from the table based on name.

        :param value: dict with format {'name': str, 'value': str}
        """
        for row in self.rows():
            if row['Name'].widget.read() == name:
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
            names_to_fill = [param['name'] for param in params_to_fill]
        except KeyError:
            raise KeyError("parameter value is missing 'name' key")

        # Check if duplicate names were passed in
        if len(set(names_to_fill)) < len(names_to_fill):
            raise ValueError(
                "Cannot use fill() with duplicate parameter names. "
                "If you wish to explicitly add a duplicate name, "
                "use CustomParameter.add()"
            )

        # Check if we need to update or remove any rows
        for row in self.rows():
            this_name = row['Name'].widget.read()
            this_value = row['Value'].widget.read()
            if this_name not in names_to_fill:
                # Delete row if its name/value is not in desired values
                row['Actions'].widget.click()  # click 'Remove' icon
            else:
                # Check if value should be updated for this name
                # First get the desired value for this param name
                desired_value = None
                for index, param in enumerate(params_to_fill):
                    if param['name'] == this_name:
                        desired_value = param['value']
                        # Since we're editing this name now, don't add it later
                        params_to_fill.pop(index)
                        break
                if desired_value is not None and this_value != desired_value:
                    # Update row's value for this name
                    row['Value'].widget.fill(desired_value)
                else:
                    # Desired parameter name/value is already filled
                    continue

        # Add the remaining values for names that were not already in the table
        for param in params_to_fill:
            self.add(param)


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
        "[*[self::span or self::i][contains(@class, 'caret')]]")
    button = Text(
        ".//*[self::button or self::span][contains(@class, 'btn')]"
        "[not(*[self::span or self::i][contains(@class, 'caret')])]")
    ITEMS_LOCATOR = './ul/li/a'
    ITEM_LOCATOR = './ul/li/a[normalize-space(.)="{}"]'

    @property
    def is_open(self):
        """Checks whether dropdown list is open."""
        return 'open' in self.browser.classes(self)

    def open(self):
        """Opens dropdown list"""
        if not self.is_open:
            self.dropdown.click()

    @property
    def items(self):
        """Returns a list of all dropdown items as strings."""
        return [
            self.browser.text(el) for el in
            self.browser.elements(self.ITEMS_LOCATOR, parent=self)]

    def select(self, item):
        """Selects item from dropdown."""
        if item in self.items:
            self.open()
            self.browser.element(
                self.ITEM_LOCATOR.format(item), parent=self).click()
        else:
            raise ValueError(
                'Specified action "{}" not found in actions list. Available'
                ' actions are {}'
                .format(item, self.items)
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
    CHECKBOX = (
        './/input[@ng-model="item.selected"][parent::label[contains(., "{}")]]'
    )

    def __init__(self, parent, locator=None, logger=None):
        """Allow to specify ``locator`` if needed or use default one otherwise.
        Locator is needed when multiple :class:`LCESelector` are present,
        typically as a part of :class:`airgun.views.common.LCESelectorGroup`.
        """
        if locator is None:
            locator = (
                ".//div[contains(@class, 'path-selector')]"
                "//ul[@class='path-list']")
        super(LCESelector, self).__init__(parent, locator, logger=logger)

    def checkbox_selected(self, locator):
        """Identify whether specific checkbox is selected or not"""
        return 'ng-not-empty' in self.browser.get_attribute(
            'class', locator, parent=self)

    def select(self, locator, value):
        """Select or deselect checkbox depends on the value passed"""
        value = bool(value)
        current_value = self.checkbox_selected(locator)
        if value == current_value:
            return False
        self.browser.click(locator, parent=self)
        if self.checkbox_selected(locator) != value:
            raise WidgetOperationFailed(
                'Failed to set the checkbox to requested value.')
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
        checkbox_name = list(value.keys())[0]
        checkbox_value = value[checkbox_name]
        checkbox_locator = self.CHECKBOX.format(checkbox_name)
        return self.select(checkbox_locator, checkbox_value)


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
            "or contains(@ng-model, 'unlimited')]"))
    limit = TextInput(
        locator=(
            ".//input[@type='number'][contains(@ng-required, 'unlimited')]"))

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
    save_button = Text(".//button[span[text()='Save']]")
    cancel_button = Text(".//button[span[text()='Cancel']]")
    entry_value = Text(".//span[contains(@class, 'editable-value')]")

    def __init__(self, parent, locator=None, name=None, logger=None):
        """Supports initialization via ``locator=`` or ``name=``"""
        if locator and name or not locator and not name:
            raise TypeError('Please specify either locator or name')
        locator = (
            locator or
            ".//dt[normalize-space(.)='{}']"
            "/following-sibling::dd[1]".format(name)
        )
        super(EditableEntry, self).__init__(parent, locator, logger)

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
        self.edit_field.fill(value)
        self.save_button.click()

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
        ".//dt[contains(., '{}')]/following-sibling::dd[not(contains("
        "@class, 'ng-hide'))][1]"
    )

    def __init__(self, parent, locator=None, name=None, logger=None):
        """Supports initialization via ``locator=`` or ``name=``"""
        if locator and name or not locator and not name:
            raise TypeError('Please specify either locator or name')
        locator = (
            locator or
            self.BASE_LOCATOR.format(name)
        )
        super(ReadOnlyEntry, self).__init__(parent, locator, logger)

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
        self.browser.execute_script(
            "ace.edit('{0}').setValue('{1}');".format(self.ace_edit_id, value))

    def read(self):
        """Returns string with current widget value"""
        return self.browser.execute_script(
            "ace.edit('{0}').getValue();".format(self.ace_edit_id))


class SatTable(Table):
    """Satellite version of table. Main difference - in case it's empty, there
    might be just 1 column with appropriate message in table body or no columns
    and rows at all.

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
    no_rows_message = (
        ".//td/span[contains(@data-block, 'no-rows-message') or "
        "contains(@data-block, 'no-search-results-message')]")
    tbody_row = Text('./tbody/tr')

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

    def read(self):
        """Return empty list in case table is empty"""
        if not self.has_rows:
            self.logger.debug('Table {} is empty'.format(self.locator))
            return []

        return super(SatTable, self).read()


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
        rows = super(
            SatSubscriptionsTable, self).rows(*extra_filters, **filters)
        if self.has_rows:
            rows = list(rows)
            self.title_rows = rows[0:][::2]
            return iter(rows[1:][::2])
        return rows

    def read(self):
        """Return content rows with 1 extra column 'Repository Name' in it."""
        read_rows = super(SatSubscriptionsTable, self).read()
        if self.has_rows:
            titles = iter(column[1].read() for column in self.title_rows)
            for row in read_rows:
                row['Repository Name'] = next(titles)
        return read_rows


class SatTableWithUnevenStructure(SatTable):
    """Applicable for every table in application that has uneven amount of
    headers and columns(usually we talk about 1 header but 2 columns)
    We taking into account that all possible content rows are actually present
    in DOM, but some are 'hidden' using css class. Also we can specify what
    widget we expect in a second column (e.g. link or text)

    Some examples where we can use current class:
    'Content Counts' table present in every repository, containing amount of
    packages/puppet modules/etc with links to corresponding details pages.
    'Properties' table present in every host details page

    Example html representation::

        <table class="table table-striped table-bordered">
            <thead>
            <tr>
              <th colspan="2" ...><span ...>Content Type</span></th>
            </tr>
            </thead>

            <tbody>
            <tr ng-show="repository.content_type === 'yum'" class="ng-hide">
              <td><span>Packages</span></td>
              <td class="align-center">
                <a ui-sref="product.repository.manage-content.packages(...)"
                 href=".../repositories/151/content/packages">
                  0
                </a></td>
            </tr>

            ...

            <tr ng-show="repository.content_type === 'puppet'" class="">
              <td><span>Puppet Modules</span></td>
              <td class="align-center">
                <a ui-sref="product.repository.manage-content.puppet-module..."
                 href=".../repositories/151/content/content/puppet_modules">
                  2
                </a></td>
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
        column_widgets = {
            1: Text(locator=column_locator)
        }
        super().__init__(
            parent,
            locator=locator,
            logger=logger,
            column_widgets=column_widgets
        )

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
        return self.browser.get_attribute(
            'aria-valuetext', self.PROGRESSBAR, check_safe=False)

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
        wait_for(
            lambda: self.is_completed is True,
            timeout=timeout,
            delay=delay,
            logger=self.logger
        )

    def read(self):
        """Returns current progress."""
        return self.progress


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
        ".//*[name()='svg']//*[name()='tspan']"
        "[contains(@class,'donut-title-small-pf')]"
    )
    chart_title_value = Text(
        ".//*[name()='svg']//*[name()='tspan']"
        "[contains(@class,'donut-title-big-pf')]"
    )

    def read(self):
        """Return dictionary that contains chart title name as key and chart
        value as its value
        """
        return {self.chart_title_text.read(): self.chart_title_value.read()}
