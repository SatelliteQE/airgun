from widgetastic.widget import Table, Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import PuppetClassesMultiSelect


class ConfigGroupsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Config Groups']")
    new = Text("//a[normalize-space(.)='Create Config Group']")
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


class ConfigGroupCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='config_group_name')
    submit = Text('//input[@name="commit"]')
    classes = PuppetClassesMultiSelect(locator='.//form')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Config Groups'
            and self.breadcrumb.locations[1] == 'Create Config Group'
        )


class ConfigGroupEditView(ConfigGroupCreateView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Config Groups'
            and self.breadcrumb.read().startswith('Edit ')
        )
