from widgetastic.widget import FileInput
from widgetastic.widget import Select
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ConfirmationDialog
from airgun.widgets import EditableEntry
from airgun.widgets import ReadOnlyEntry


class ContentCredentialsTableView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Content Credentials')]")
    new = Text("//button[contains(@href, '/content_credentials/new')]")
    table = Table('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ContentCredentialCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    content_type = Select(id='content_type')
    content = TextInput(name='content')
    upload_file = FileInput(name='file_path')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Credential'
            and self.breadcrumb.read() == 'New Content Credential'
        )


class ContentCredentialEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    remove = Text("//button[contains(., 'Remove Content Credential')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Content Credential'
            and self.breadcrumb.read() != 'New Content Credential'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        content_type = ReadOnlyEntry(name='Type')
        content = EditableEntry(name='Content')
        products = ReadOnlyEntry(name='Products')
        repos = ReadOnlyEntry(name='Repositories')

    @View.nested
    class products(SatTab, SearchableViewMixin):
        table = Table('.//table', column_widgets={'Name': Text('./a')})

    @View.nested
    class repositories(SatTab, SearchableViewMixin):
        table = Table('.//table', column_widgets={'Name': Text('./a')})
