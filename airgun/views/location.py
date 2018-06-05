from widgetastic.widget import Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    SatTable,
)


class LocationsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Locations']")
    new = Text("//a[contains(@href, '/locations/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class LocationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='location_name')
    description = TextInput(id='location_description')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Locations'
                and self.breadcrumb.read() == 'New Location'
        )
