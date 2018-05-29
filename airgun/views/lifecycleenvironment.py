from widgetastic.widget import (
    ParametrizedView,
    ParametrizedLocator,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab
from airgun.widgets import EditableEntry, ReadOnlyEntry, SatTable


class LCEView(BaseLoggedInView, ParametrizedView):
    title = Text("//h2[contains(., 'Lifecycle Environment Paths')]")
    new_path = Text(
        "//a[contains(@href, '/lifecycle_environments') "
        "and contains(@href, 'new') and contains(@class, 'btn-primary')]"
    )
    edit_parent_env = Text(
        "//table[contains(@class, 'info-blocks')]"
        "//a[contains(@ui-sref, 'environment.details')]"
    )
    parent_env_cvs_count = Text(
        "//table[contains(@class, 'info-blocks')]"
        "//td[span[contains(., 'Content Views')]]/div")
    parent_env_products_count = Text(
        "//table[contains(@class, 'info-blocks')]"
        "//td[span[contains(., 'Products')]]/div")
    parent_env_products_errata = Text(
        "//table[contains(@class, 'info-blocks')]"
        "//td[span[contains(., 'Errata')]]/div")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    @View.nested
    class lce(ParametrizedView):
        ROOT = ParametrizedLocator(
            ".//div[@ng-repeat='path in paths']"
            "[table//th/a[normalize-space(.)='{lce_name}']]"
        )
        PARAMETERS = ('lce_name',)
        LAST_ENV = "//div[@ng-repeat='path in paths']//table//th[last()]"
        current_env = Text(ParametrizedLocator(
            ".//a[normalize-space(.)='{lce_name}']"))
        envs_table = SatTable(locator=".//table")
        new_child = Text(".//a[contains(@href, '/lifecycle_environments/')]")

        @classmethod
        def all(cls, browser):
            """Helper method which returns list of tuples with all available
            LCE names (last available environment is used as a name). It's
            required for :meth:`read` to work properly.
            """
            return [
                (element.text,) for element in browser.elements(cls.LAST_ENV)]

        def read(self):
            """Returns content views and count hosts count per each available
            lifecycle environment
            We get dictionary in next format:

                {
                    'LCE_1': {'Content Views': 0, 'Content Hosts': 1},
                    'LCE_2': {'Content Views': 1, 'Content Hosts': 2},
                }

            """
            result = {}
            available_envs = self.envs_table.headers[1:]
            lce_metric_names = [row[0].text for row in self.envs_table]
            for column_name in available_envs:
                metric_values = (
                    int(row[column_name].text) for row in self.envs_table)
                result[column_name] = {}
                for row_name in lce_metric_names:
                    result[column_name][row_name] = next(metric_values)
            return result


class LCECreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    label = TextInput(id='label')
    description = TextInput(id='description')
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Environments List'
                and self.breadcrumb.read() == 'New Environment'
        )


class LCEEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Environments'
                and self.breadcrumb.read() != 'New Environment'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        label = ReadOnlyEntry(name='Label')
        description = EditableEntry(name='Description')
