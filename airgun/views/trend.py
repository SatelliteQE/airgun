from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.widgets import ActionsDropdown
from airgun.widgets import FilteredDropdown


class TrendsView(BaseLoggedInView):
    title = Text("//h1[text()='Trends']")
    welcome_page = Text("//div[@class='blank-slate-pf']")
    new = Text("//a[contains(@href, '/trends/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Action': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class TrendCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    trendable_type = FilteredDropdown(id='trend_trendable_type')
    trendable_id = FilteredDropdown(id='trend_trendable_id')
    name = TextInput(id='trend_name')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Trends'
            and self.breadcrumb.read() == 'Create Trend'
        )


class TrendEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    table = Table(
        './/table',
        column_widgets={
            'Display Name': TextInput(locator=".//input[@type='text']"),
        },
    )
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Trends'
            and self.breadcrumb.read().startswith('Edit ')
        )
