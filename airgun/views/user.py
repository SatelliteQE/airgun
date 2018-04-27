from widgetastic.widget import Checkbox, Text, TextInput, View

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import FilteredDropdown, MultiSelect


class UserView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Users']")
    new = Text("//a[contains(@href, '/users/new')]")
    edit = Text("//a[contains(@href, 'edit') and contains(@href, 'users')]")
    delete = Text("//a[contains(@href, '/users/') and @data-method='delete']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class UserDetailsView(BaseLoggedInView):
    form = Text("//form[@id='new_user' or contains(@id, 'edit_user')]")
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.form, exception=False) is not None

    @View.nested
    class user(SatTab):
        login = TextInput(id='user_login')
        firstname = TextInput(id='user_firstname')
        lastname = TextInput(id='user_lastname')
        mail = TextInput(id='user_mail')
        description = TextInput(id='user_description')
        language = FilteredDropdown(id='user_locale')
        timezone = FilteredDropdown(id='user_timezone')
        auth = FilteredDropdown(id='user_auth_source')
        password = TextInput(id='user_password')
        confirm = TextInput(id='password_confirmation')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-user_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-user_organization_ids')

    @View.nested
    class roles(SatTab):
        admin = Checkbox(id='user_admin')
        resources = MultiSelect(id='ms-user_role_ids')
