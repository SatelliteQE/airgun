from widgetastic.widget import Checkbox, Text, TextInput, View

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import EditableEntry, SatTable


class HostCollectionView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Host Collections')]")
    new = Text("//button[contains(@href, '/host_collections/new')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class HostCollectionDetailsView(BaseLoggedInView):
    name = TextInput(id='name')
    unlimited_hosts = Checkbox(name='limit')
    max_hosts = TextInput(id='max_hosts')
    description = TextInput(id='description')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class HostCollectionEditView(BaseLoggedInView):
    title = Text("//h3[contains(., 'Basic Information')]")
    name = EditableEntry(name='Name')
    description = EditableEntry(name='Description')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    @View.nested
    class hosts(SatTab):
        TAB_NAME = 'Hosts'

        resources = View.nested(AddRemoveResourcesView)
