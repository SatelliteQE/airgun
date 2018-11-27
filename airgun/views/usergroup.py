from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import MultiSelect, SatTable


class UserGroupsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='User Groups']")
    new = Text("//a[contains(@href, '/usergroups/new')]")
    table = SatTable(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Actions': Text('.//a[@data-method="delete"]'),
            }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
                self.title, exception=False) is not None


class UserGroupDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
                self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Usergroups'
                and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class usergroup(SatTab):
        TAB_NAME = "User Group"

        name = TextInput(id='usergroup_name')
        usergroups = MultiSelect(id='ms-usergroup_usergroup_ids')
        users = MultiSelect(id='ms-usergroup_user_ids')

    @View.nested
    class roles(SatTab):
        admin = Checkbox(id='usergroup_admin')
        resources = MultiSelect(id='ms-usergroup_role_ids')


class UserGroupCreateView(UserGroupDetailsView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
                self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Usergroups'
                and self.breadcrumb.read() == 'Create User group'
        )
