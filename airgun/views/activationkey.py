from widgetastic.widget import Checkbox, Text, TextInput

from airgun.views.common import BaseLoggedInView, SearchableViewMixin


class ActivationKeyView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Activation Keys')]")
    new = Text("//button[contains(@href, '/activation_keys/new')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ActivationKeyDetailsView(BaseLoggedInView):
    name = TextInput(id='name')
    description = TextInput(id='description')
    unlimited_hosts = Checkbox(name='limit')
    max_hosts = TextInput(id='max_hosts')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None
