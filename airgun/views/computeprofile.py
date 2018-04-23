from widgetastic.widget import Text, TextInput, Widget
from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class ClickOnArrowButton(Widget):

    # TODO use the generic dropdown
    ROOT = ".//table//div[contains(@class, 'btn-group')]"
    open_dropdown = Text(".//a[contains(@data-toggle, 'dropdown')]")
    delete = Text(".//a[contains(@data-method, 'delete') and "
                  "contains(@href, '/compute_profiles/')]")

    def fill(self, value):
        self.open_dropdown.click()
        self.delete.click(handle_alert=True)


class ComputeProfileView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compute Profiles']")
    new = Text("//a[contains(@href, '/compute_profiles/new')]")
    rename = Text("//a[contains(@href, '/compute_profiles/') and "
                  "contains(@href, 'edit')]")
    action_list = ClickOnArrowButton()

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
