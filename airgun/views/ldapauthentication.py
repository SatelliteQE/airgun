from widgetastic.widget import Checkbox, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab
from airgun.widgets import FilteredDropdown, MultiSelect, SatTable


class LDAPAuthenticationsView(BaseLoggedInView):
    title = Text(
        "//h1[text()='LDAP authentication sources' or "
        "text()='LDAP Authentication']"
    )
    new = Text("//a[contains(@href, '/auth_source_ldaps/new')]")
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


class LDAPAuthenticationCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Auth source ldaps'
                and self.breadcrumb.read() == 'Create LDAP Auth Source'
        )

    @View.nested
    class ldap_server(SatTab):
        TAB_NAME = 'LDAP server'

        name = TextInput(id='auth_source_ldap_name')
        host = TextInput(id='auth_source_ldap_host')
        text_connection = Text('//a[@id="test_connection_button"]')
        ldaps = Checkbox(id='auth_source_ldap_tls')
        port = TextInput(id='auth_source_ldap_port')
        server_type = FilteredDropdown(id='auth_source_ldap_server_type')

    @View.nested
    class account(SatTab):
        account_name = TextInput(id='auth_source_ldap_account')
        password = TextInput(id='auth_source_ldap_account_password')
        base_dn = TextInput(id='auth_source_ldap_base_dn')
        groups_base_dn = TextInput(id='auth_source_ldap_groups_base')
        use_netgroups = Checkbox(id='auth_source_ldap_use_netgroups')
        ldap_filter = TextInput(id='auth_source_ldap_ldap_filter')
        onthefly_register = Checkbox(id='auth_source_ldap_onthefly_register')
        usergroup_sync = Checkbox(id='auth_source_ldap_usergroup_sync')

    @View.nested
    class attribute_mappings(SatTab):
        TAB_NAME = 'Attribute mappings'

        login = TextInput(id='auth_source_ldap_attr_login')
        first_name = TextInput(id='auth_source_ldap_attr_firstname')
        last_name = TextInput(id='auth_source_ldap_attr_lastname')
        mail = TextInput(id='auth_source_ldap_attr_mail')
        photo = TextInput(id='auth_source_ldap_attr_photo')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-auth_source_ldap_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-auth_source_ldap_organization_ids')


class LDAPAuthenticationEditView(LDAPAuthenticationCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Auth source ldaps'
                and self.breadcrumb.read().startswith('Edit LDAP-')
        )
