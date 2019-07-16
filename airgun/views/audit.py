from widgetastic.widget import Text, View
from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Search, SatTableWithoutHeaders


class AuditEntry(View):

    ROOT = ".//div[@id='audit-list']/div/div[contains(@class, 'list-group-item')]"
    user = Text(".//a[@class='user-info']")
    action_type = Text(".//div[@class='list-group-item-text' and text()]")
    resource_type = Text(".//div[@class='list-view-pf-additional-info-item'][1]")
    resource_name = Text(".//div[@class='list-view-pf-additional-info-item'][2]")
    created_at = Text(".//div[@class='list-view-pf-actions']/span")
    expander = Text(".//div[contains(@class, 'list-view-pf-expand')]/span")
    affected_organization = Text(
        ".//div[normalize-space(.) = 'Affected Organizations']/following-sibling::div")
    affected_location = Text(
        ".//div[normalize-space(.) = 'Affected Locations']/following-sibling::div")
    action_summary = SatTableWithoutHeaders('.//table')
    comment = Text(".//p[@class='comment-desc']")

    @property
    def expanded(self):
        return 'fa-angle-down' in self.browser.classes(self.expander)

    def read(self):
        if not self.expanded:
            self.expander.click()
        return super().read()

    def fill(self, values):
        raise ReadOnlyWidgetError('View is read only, fill is prohibited')


class AuditsView(BaseLoggedInView):
    title = Text("//h1[text()='Audits']")
    searchbox = Search()
    entry = AuditEntry()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def search(self, query):
        self.searchbox.search(query)
        return self.entry.read()
