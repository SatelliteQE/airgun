from widgetastic.widget import Checkbox
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Button as P4Button

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import FilteredDropdown
from airgun.widgets import MultiSelect


class UserGroupsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='User Groups']")
    new_on_blank_page = P4Button('Create User group')
    new = Text("//a[contains(@href, '/usergroups/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class UserGroupDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'User Groups'
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

    @View.nested
    class external_groups(SatTab):
        TAB_NAME = 'External Groups'
        table = Table(
            './/table',
            column_widgets={
                'Actions': Text('.//a[contains(@href, "refresh")]'),
            },
        )

        add_external_user_group = Text('.//a[@data-association="external_usergroups"]')
        name = TextInput(
            locator=(
                "(//input[starts-with(@name, 'usergroup[external_usergroups_attributes]')]"
                "[contains(@name, '[name]')])[last()]"
            )
        )
        auth_source = FilteredDropdown(
            locator=(
                "//div[starts-with(@id, 's2id_usergroup_external_usergroups_attributes')]"
                "[contains(@id, 'auth_source_id')]"
            )
        )

        def before_fill(self, values):
            self.add_external_user_group.click()


class UserGroupCreateView(UserGroupDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'User Groups'
            and self.breadcrumb.read() == 'Create User group'
        )
