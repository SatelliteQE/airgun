from widgetastic.widget import Text, View

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4
from airgun.widgets import SatTableWithoutHeaders


class AuditEntry(View):
    ROOT = ".//div[@id='audit-list']/ul/li"
    user = Text(".//a[@class='user-info']")
    action_type = Text(".//div[contains(@class, 'pf-v5-c-data-list__cell')][2]")
    resource_type = Text(".//div[contains(@class, 'item-name')]")
    resource_name = Text(".//div[contains(@class, 'item-resource')]")
    created_at = Text(".//div[contains(@class, 'audits-list-actions')]/span")
    expander = Text(".//*[@aria-label='Details']")
    affected_organization = Text(
        "(.//a[@data-ouia-component-id='taxonomy-inline-btn'])[1]"
    )
    affected_location = Text("(.//a[@data-ouia-component-id='taxonomy-inline-btn'])[2]")
    action_summary = SatTableWithoutHeaders(".//table")
    comment = Text(".//p[@class='comment-desc']")

    @property
    def expanded(self):
        return self.browser.get_attribute("aria-expanded", self.expander) == "true"

    def read(self):
        if not self.expanded:
            self.expander.click()
        return super().read()

    def fill(self, values):
        raise ReadOnlyWidgetError("View is read only, fill is prohibited")


class AuditsView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Audits']")
    table = AuditEntry()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
