from widgetastic.widget import Table, Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
)
from airgun.widgets import SatTableWithUnevenStructure


class ModuleStreamView(BaseLoggedInView, SearchableViewMixin):
    """Main Module_Streams view"""

    title = Text('//h1[contains(., "Module Streams")]')
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        """The view is displayed when it's title exists"""
        return self.title.is_displayed


class ModuleStreamsDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    # TODO Add `title` after SAT-41764 is resolved
    details_tab = Text("//a[@id='module-stream-tabs-container-tab-1']")

    @property
    def is_displayed(self):
        """Assume the view is displayed when its breadcrumb is visible"""
        breadcrumb_loaded = self.breadcrumb.is_displayed
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Module Streams'

    @View.nested
    class details(SatTab):
        details_table = SatTableWithUnevenStructure(locator='.//table', column_locator='./*')

    @View.nested
    class repositories(SatTab):
        table = Table(
            locator='.//table',
            column_widgets={
                'Name': Text('./a'),
            },
        )
