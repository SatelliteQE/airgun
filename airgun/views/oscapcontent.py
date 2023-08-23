from widgetastic.widget import FileInput, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import ActionsDropdown, MultiSelect, SatTable


class SCAPContentsView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='SCAP Content']")
    new = Text("//a[contains(@href, 'scap_contents/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Title': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class SCAPContentCreateView(BaseLoggedInView):
    create_form = Text("//form[@id='new_scap_content']")
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[normalize-space(.)="Cancel"]')

    @View.nested
    class file_upload(SatTab):
        TAB_NAME = 'File Upload'
        title = TextInput(id='scap_content_title')
        scap_file = FileInput(id='scap_content_scap_file')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-scap_content_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-scap_content_organization_ids')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.create_form, exception=False) is not None


class SCAPContentEditView(SCAPContentCreateView):
    scap_file_name = Text('//div[@class="col-md-4"]/b')
    breadcrumb = BreadCrumb()

    @View.nested
    class file_upload(SatTab):
        TAB_NAME = 'File Upload'
        title = TextInput(id='scap_content_title')
        uploaded_scap_file = Text(locator="//label[@for='scap_file']/following-sibling::div/b")
        scap_file = FileInput(id='scap_content_scap_file')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Scap Contents'
