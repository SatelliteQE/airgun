from widgetastic.widget import Table, Text
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class HostFactView(BaseLoggedInView, SearchableViewMixin):
    breadcrumb = BreadCrumb()

    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
        },
    )
    expand_fact_value = Text(
        "//div/a[contains(@class, 'pf-v5-c-button') or contains(span/@class, 'pf-v5-c-icon')]"
    )

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.breadcrumb.is_displayed
        return breadcrumb_loaded and self.breadcrumb.read().startswith('Facts Values')
