from widgetastic.widget import (
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SatTable,
    SearchableViewMixin,
)
from airgun.widgets import (
    FilteredDropdown,
)


class HostGroupTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[contains(., 'Host Groups')]")
    new = Text("//a[contains(@href, '/hostgroups/new')]")
    table = SatTable(
        locator='.//table',
        column_widgets={
            'Name': Text("//a[starts-with(@href, '/hostgroups/') and \
                contains(@href,'/edit')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostGroupCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text("//input[@name='commit']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Hostgroups'
            and self.breadcrumb.read() == 'Create Host Group'
        )

    @View.nested
    class hostgroup(SatTab):
        TAB_NAME = 'Host Group'
        name = TextInput(id='hostgroup_name')
        puppet_environment = FilteredDropdown(
            id='s2id_hostgroup_environment_id')
