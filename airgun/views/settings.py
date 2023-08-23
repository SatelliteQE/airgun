from wait_for import wait_for
from widgetastic.widget import Table, Text
from widgetastic_patternfly import Button

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import PopOverWidget


class SettingsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Settings']")
    table = Table(
        './/table',
        column_widgets={'Value': PopOverWidget()},
    )

    @SatTab.nested
    class Email(SatTab):
        test_email_button = Button(id="test_mail_button")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    def wait_for_update(self):
        """Wait for value to update"""
        wait_for(
            lambda: self.table.row()['Value'].widget.is_displayed,
            timeout=30,
            delay=1,
            logger=self.logger,
        )
