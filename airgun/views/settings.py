from wait_for import wait_for
from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import PopOverWidget, SatTable


class SettingsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Settings']")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('.//a'),
            'Value': Text('.//span[contains(@class, "editable-click")]')
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SettingEditView(SettingsView):
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('.//a'),
            'Value': PopOverWidget(
                './/span[contains(@class, "editable-click")]')
        },
    )

    def wait_for_update(self):
        """Wait for value to update"""
        wait_for(
            lambda: not self.table.row()['Value'].widget.header.is_displayed,
            timeout=10,
            delay=1,
            logger=self.logger,
        )

    def check_for_error(self):
        """Check for error while updating"""
