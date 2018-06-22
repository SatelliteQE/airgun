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
    ActionsDropdown,
    MultiSelect,
)


class PuppetEnvironmentsTableView(BaseLoggedInView, SearchableViewMixin):
    """
    Basic view after clicking Configure -> Environments.
    In basic view, there can be seen title Puppet Environments, button
    Create Puppet Environment (new) and table with existing Puppet Environments
    """
    title = Text("//h1[contains(., 'Puppet Environments')]")
    new = Text("//a[contains(@href, '/environments/new')]")
    table = SatTable(
        locator='.//table',
        column_widgets={
            'Name': Text("//a[starts-with(@href, '/environments/') and \
                contains(@href,'/edit')]"),
            'Actions': ActionsDropdown(
                './div[contains(@class, "btn-group")]')
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class PuppetEnvironmentCreateView(BaseLoggedInView):
    """
    Details view of the page with boxes that have to be filled in to
    create a new puppet environment
    """
    breadcrumb = BreadCrumb()
    submit = Text("//input[@name='commit']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Environments'
            and self.breadcrumb.read() == 'Create Environment'
        )

    @View.nested
    class environment(SatTab):
        name = TextInput(id='environment_name')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-environment_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-environment_organization_ids')
