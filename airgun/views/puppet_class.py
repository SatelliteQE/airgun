from widgetastic.widget import Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.smart_variable import SmartVariableContent
from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import MultiSelect, SatTable


class PuppetClassesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Puppet Classes']")
    import_environments = Text("//a[contains(@href, '/import_environments')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Class name': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class PuppetClassDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Puppetclasses'
            and self.breadcrumb.read().starts_with('Edit Puppet Class ')
        )

    @View.nested
    class puppet_class(SatTab):
        TAB_NAME = 'Puppet Class'
        # Name field is disabled by default
        name = TextInput(id='puppetclass_name')
        # Puppet environment field is disabled by default
        puppet_environment = TextInput(id='puppetclass_environments')
        host_group = MultiSelect(id='ms-puppetclass_hostgroup_ids')

    @View.nested
    class smart_class_parameter(SatTab):
        TAB_NAME = 'Smart Class Parameter'
        pass

    @View.nested
    class smart_class_variables(SatTab):
        TAB_NAME = 'Smart Variables'
        variable = SmartVariableContent(
            locator="//div[@class='tab-pane fields active']")
