from widgetastic.widget import Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import FilteredDropdown, MultiSelect


class MediumView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Installation Media']")
    new = Text("//a[contains(@href, '/media/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class MediaCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Installation Media'
            and self.breadcrumb.read() == 'Create Medium'
        )

    @View.nested
    class medium(SatTab):
        name = TextInput(id='medium_name')
        path = TextInput(id='medium_path')
        os_family = FilteredDropdown(id='medium_os_family')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-medium_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-medium_organization_ids')


class MediaEditView(MediaCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Installation Media'
            and self.breadcrumb.read().startswith('Edit ')
        )
