from widgetastic.widget import Checkbox
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import SatTable


class BookmarksView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Bookmarks']")
    table = SatTable(
        ".//table",
        column_widgets={
            'Name': Text('./a'),
            'Actions': Text("./span/a"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class BookmarkEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='bookmark_name')
    query = TextInput(id='bookmark_query')
    public = Checkbox(id='bookmark_public')
    submit = Text(".//input[@type='submit']")
    cancel = Text(".//a[text()='Cancel']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Bookmarks'
            and self.breadcrumb.read().startswith('Edit')
        )
