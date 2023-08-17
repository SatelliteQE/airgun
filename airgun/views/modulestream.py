from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SatTable
from airgun.views.common import SearchableViewMixinPF4
from airgun.widgets import SatTableWithUnevenStructure


class ModuleStreamView(BaseLoggedInView, SearchableViewMixinPF4):
    """Main Module_Streams view"""

    title = Text("//h2[contains(., 'Module Streams')]")
    table = SatTable('.//table', column_widgets={'Name': Text("./a")})

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ModuleStreamsDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    title = Text("//a(., 'Module Streams')]")
    details_tab = Text("//a[@id='module-stream-tabs-container-tab-1']")

    @property
    def is_displayed(self):
        """Assume the view is displayed when its breadcrumb is visible"""
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Module Streams'

    @View.nested
    class details(SatTab):
        details_table = SatTableWithUnevenStructure(locator='.//table', column_locator='./*')

    @View.nested
    class repositories(SatTab):
        table = Table(
            locator=".//table",
            column_widgets={
                'Name': Text("./a"),
            },
        )
