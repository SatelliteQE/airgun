from widgetastic.widget import Text, TextInput
from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import ActionsDropdown


class ComputeProfileView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compute Profiles']")
    new = Text("//a[contains(@href, '/compute_profiles/new')]")
    rename = Text("//a[contains(@href, '/compute_profiles/') and "
                  "contains(@href, 'edit')]")
    actions = ActionsDropdown("//td//div[contains(@class, 'btn-group')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ComputeProfileDetailsView(BaseLoggedInView):
    name = TextInput(locator=".//input[@id='compute_profile_name']")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None
