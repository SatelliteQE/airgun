from widgetastic.widget import (
    FileInput,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    MultiSelect,
    SatTable,
)


class SCAPTailoringFilesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Tailoring Files']")
    new = Text("//a[contains(@href, 'tailoring_files/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Title': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SCAPTailoringFileCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[text()="Cancel"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Tailoring files'
                and self.breadcrumb.read() == 'Upload new Tailoring File'
        )

    @View.nested
    class file_upload(SatTab):
        TAB_NAME = 'File Upload'
        name = TextInput(id='tailoring_file_name')
        scap_file = FileInput(id='tailoring_file_scap_file')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-tailoring_file_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-tailoring_file_organization_ids')


class SCAPTailoringFileEditView(SCAPTailoringFileCreateView):
    scap_file_name = Text(
        '//label[contains(., "Scap File")]/following-sibling::div/b')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Tailoring files'
                and self.breadcrumb.read() != 'Upload new Tailoring File'
        )
