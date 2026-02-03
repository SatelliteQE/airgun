from widgetastic.widget import Checkbox, Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import SatTable


class BookmarksView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Bookmarks']")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': Text('./span/a'),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class BookmarkEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='bookmark_name')
    query = TextInput(id='bookmark_query')
    public = Checkbox(id='bookmark_public')
    submit = Text(".//input[@type='submit']")
    cancel = Text(".//a[normalize-space(.)='Cancel']")

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Bookmarks'
            and self.breadcrumb.read().startswith('Edit')
        )
