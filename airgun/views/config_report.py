from widgetastic.widget import Text
from widgetastic_patternfly import BreadCrumb, Button

from airgun.views.common import BaseLoggedInView, SatTable, SearchableViewMixin


class ConfigReportsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Reports']")
    export = Button("Export")
    table = SatTable(
        ".//table",
        column_widgets={
            "Last report": Text("./a"),
            "Actions": Text('.//a[@data-method="delete"]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ConfigReportDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False
        )
        return breadcrumb_loaded and self.breadcrumb.locations[0] == "Config Reports"

    delete = Button("Delete")
    host_details = Button("Host details")
