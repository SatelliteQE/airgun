from wait_for import wait_for
from widgetastic.widget import Text

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import PopOverWidget, Table


class SettingsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Settings']")
    table = Table(
        './/table',
        column_widgets={
            'Value': PopOverWidget(
                './/span[contains(@class, "editable-click")]')
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def wait_for_update(self):
        """Wait for value to update"""
        wait_for(
            lambda: not self.table.row()['Value'].widget.header.is_displayed,
            timeout=30,
            delay=1,
            logger=self.logger,
        )
