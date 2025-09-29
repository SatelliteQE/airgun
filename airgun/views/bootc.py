from widgetastic.widget import Table, Text, View
from widgetastic_patternfly4.ouia import ExpandableTable

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixinPF4,
)


class BootedContainerImagesView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text('.//h1[@data-ouia-component-id="header-text"]')

    # This represents the contents of the expanded table rows
    class NestedBootCTable(View):
        table = Table(
            locator='.//div[@class="pf-c-table__expandable-row-content"]/table',
            column_widgets={"Image Digest": Text("./a"), "Hosts": Text("./a")},
        )

    # Passing in the nested table as content_view, refer to ExpandableTable docs for info
    table = ExpandableTable(
        component_id="booted-containers-table",
        column_widgets={
            "Image Name": Text("./a"),
            "Image Digests": Text("./a"),
            "Hosts": Text("./a"),
        },
        content_view=NestedBootCTable(),
    )

    @property
    def is_displayed(self):
        return self.table.is_displayed
