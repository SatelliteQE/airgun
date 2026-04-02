from widgetastic.widget import Text
from widgetastic_patternfly5 import Pagination as PF5Pagination
from widgetastic_patternfly5.ouia import PatternflyTable

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class ContentCredentialsNewTableView(BaseLoggedInView, SearchableViewMixinPF4):
    """View for the React-based Content Credentials list page at /labs/content_credentials."""

    title = Text("//h1[normalize-space(.)='Content Credentials']")

    table = PatternflyTable(
        component_id='content-credentials-table',
        column_widgets={
            'Name': Text('.//td[1]'),
            'Organization': Text('.//td[2]'),
            'Type': Text('.//td[3]'),
            'Products': Text('.//td[4]'),
            'Repositories': Text('.//td[5]'),
            'Alternate Content Sources': Text('.//td[6]'),
        },
    )
    pagination = PF5Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
