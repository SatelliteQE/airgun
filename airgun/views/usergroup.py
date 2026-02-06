from widgetastic.widget import Checkbox, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly5 import Button

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import FilteredDropdown, MultiSelect


class UserGroupsView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='User Groups']")
    new_on_blank_page = Button('Create User group')
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
        return self.title.is_displayed


class UserGroupDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'User Groups'
            and self.breadcrumb.read().startswith('Edit ')
        )

    @View.nested
    class usergroup(SatTab):
        TAB_NAME = 'User Group'

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
            # this locator fails when there are multiple user groups, it doesn't specify which
            locator=("//span[contains(@class, 'select2-selection__rendered')]")
        )

        def before_fill(self, values):
            self.add_external_user_group.click()


class UserGroupCreateView(UserGroupDetailsView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'User Groups'
            and self.breadcrumb.read() == 'Create User group'
        )
