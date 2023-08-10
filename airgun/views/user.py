from widgetastic.widget import Checkbox
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixinPF4
from airgun.widgets import FilteredDropdown
from airgun.widgets import MultiSelect


class UsersView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Users']")
    new = Text("//a[contains(@href, '/users/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Username': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class UserDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Users'
            and self.breadcrumb.read().startswith('Edit ')
        )

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


class UserCreateView(UserDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Users'
            and self.breadcrumb.read() == 'Create User'
        )
