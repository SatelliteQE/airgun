from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import EditableEntry, SatTable


class HostCollectionsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Host Collections')]")
    new = Text("//button[contains(@href, '/host_collections/new')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    unlimited_hosts = Checkbox(name='limit')
    max_hosts = TextInput(id='max_hosts')
    description = TextInput(id='description')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Host Collections'
                and self.breadcrumb.read() == 'New Host Collection'
        )


class HostCollectionEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Host Collections'
                and self.breadcrumb.read() != 'New Host Collection'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        description = EditableEntry(name='Description')

    @View.nested
    class hosts(SatTab):
        TAB_NAME = 'Hosts'

        resources = View.nested(AddRemoveResourcesView)
