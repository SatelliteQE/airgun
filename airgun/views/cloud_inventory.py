from selenium.common.exceptions import NoSuchElementException
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly import Button
from widgetastic_patternfly import ItemsList
from widgetastic_patternfly import ListItem
from widgetastic_patternfly import Tab

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Search


class InventoryTab(Tab):
    """Cloud Inventory Upload Tab element.

    This is lightweight subclass needed because Cloud Inventory Upload
    tabs contain icons, and widgetastic_patternfly Tab looks for exact match.
    """
    TAB_LOCATOR = ParametrizedLocator(
        './/ul[contains(@class, "nav-tabs")]/'
        'li[./a[contains(normalize-space(.), {@tab_name|quote})]]'
    )

    def child_widget_accessed(self, widget):
        super().child_widget_accessed(widget)
        wait_for(
            lambda: widget.parent.is_displayed,
            timeout=5,
            delay=1,
            logger=widget.logger
        )


class InventoryBootstrapSwitch(Widget):
    """ Checkbox-like Switch control, representing On and Off state. But with
    fancy UI and without any <form> elements.
    There's also BootstrapSwitch widget in widgetastic_patternfly, but we don't
    inherit from it as it uses completely different HTML structure than this one
    (it has underlying <input>).
    """

    ON_TOGGLE = ".//span[contains(@class, 'bootstrap-switch-handle-on')]"
    OFF_TOGGLE = ".//span[contains(@class, 'bootstrap-switch-handle-off')]"

    def __init__(self, parent, class_name, **kwargs):
        Widget.__init__(self, parent, logger=kwargs.pop('logger', None))
        self.class_name = class_name

    def __locator__(self):
        return f"//div[@class='{self.class_name}']/div"

    @property
    def selected(self):
        classes = self.browser.classes(self)
        return 'bootstrap-switch-on' in classes

    @property
    def is_displayed(self):
        return self.browser.is_displayed(locator=self.__locator__())

    @property
    def _clickable_el(self):
        """ In automation, you need to click on exact toggle element to trigger action

        Returns: selenium webelement
        """
        locator = self.ON_TOGGLE
        if not self.selected:
            locator = self.OFF_TOGGLE
        return self.browser.element(locator=locator)

    def fill(self, value):
        value = bool(value)
        current_value = self.selected
        if value == current_value:
            return False
        else:
            self.browser.click(self._clickable_el)
            return True

    def read(self):
        return self.selected


class InventoryItem(ListItem):
    """Item related to one organization on Cloud Inventory Upload page."""
    ROOT = ParametrizedLocator(
        './/div[contains(concat(" ",@class," "), " list-group-item ") and position()={index}]'
    )
    DESCRIPTION_LOCATOR = './/div[contains(@class, "pf-description")]'
    STATUS_ELEMENTS = (
        './/div[contains(@class, "status")][contains(@class, "container")]'
        '/div[contains(@class, "item")]'
    )

    @View.nested
    class generating(InventoryTab):
        process = Text(".//div[contains(@class, 'tab-header')]/div[1]")
        restart = Button('Restart')
        terminal = Text(".//div[@class='terminal']")
        scheduled_run = Text(".//div[contains(@class, 'scheduled_run')]")

    @View.nested
    class uploading(InventoryTab):
        process = Text(".//div[contains(@class, 'tab-header')]/div[1]")
        download_report = Button('contains', 'Download Report')
        terminal = Text(".//div[@class='terminal']")

    @property
    def is_generating(self):
        try:
            self.parent_browser.selenium.find_element_by_xpath(f"{self.STATUS_ELEMENTS}[1]/div")
            return True
        except NoSuchElementException:
            return False

    @property
    def is_uploading(self):
        try:
            self.parent_browser.selenium.find_element_by_xpath(f"{self.STATUS_ELEMENTS}[2]/div")
            return True
        except NoSuchElementException:
            return False

    @property
    def status(self):
        if self.is_generating:
            return "generating"
        if self.is_uploading:
            return "uploading"
        return "idle"

    @property
    def is_active(self):
        classes = self.browser.classes(self)
        return any(['expand-active' in class_ for class_ in classes])

    def child_widget_accessed(self, widget):
        if not self.is_active:
            self.open()

    def read(self):
        return {
            'generating': self.generating.read(),
            'uploading': self.uploading.read(),
            'status': self.status,
            'allow_auto_upload': self.parent.parent.allow_auto_upload.read(),
            'obfuscate_host_names': self.parent.parent.obfuscate_host_names.read(),
        }

    def fill(self, values):
        raise ReadOnlyWidgetError('View is read only, fill is prohibited')


class CloudInventoryListView(BaseLoggedInView):
    """Main RH Cloud Inventory Upload view."""
    title = Text("//h1[@class='inventory_title']")
    searchbox = Search()
    allow_auto_upload = InventoryBootstrapSwitch(class_name='auto_upload_switcher')
    obfuscate_host_names = InventoryBootstrapSwitch(class_name='host_obfuscation_switcher')

    @View.nested
    class inventory_list(ItemsList):
        item_class = InventoryItem

        @property
        def widget_names(self):
            return [item.description for item in self.items()]

        def read(self):
            return {
                item.description: item.read()
                for item in self.items()
            }

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None
