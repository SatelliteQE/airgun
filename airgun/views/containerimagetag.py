from widgetastic.widget import Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
    TaskDetailsView,
)
from airgun.widgets import SatTable


class ContainerImageTagsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2/span[contains(., 'Container Image Tags')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ContainerImageTagReadDetailsView(TaskDetailsView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Container Image Tags'
            and len(self.breadcrumb.locations) >= 2
        )

    @View.nested
    class details(SatTab):
        product_name = Text("//a[contains(@ui-sref, 'product.info')]")
        repository_name = Text("//a[contains(@ui-sref, 'product.repository')]")

    @View.nested
    class lce(SatTab):
        TAB_NAME = 'Lifecycle Environments'
        table = SatTable(
            './/table',
            column_widgets={
                'Environment': Text('./a'),
                'Content View Version': Text('./a')
            })
