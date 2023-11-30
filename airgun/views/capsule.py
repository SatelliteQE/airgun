from widgetastic.widget import (
    Select,
    Text,
    TextInput,
    View,
)
from widgetastic_patternfly import BreadCrumb, Button
from widgetastic_patternfly4 import (
    Dropdown,
    Pagination,
)
from widgetastic_patternfly4.ouia import (
    Button as OUIAButton,
    ExpandableTable,
)

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixinPF4,
)
from airgun.widgets import (
    ActionsDropdown,
    FilteredDropdown,
    ItemsList,
    MultiSelect,
    Pf4ConfirmationDialog,
    SatTable,
)


class DeleteCapsuleConfirmationDialog(Pf4ConfirmationDialog):
    confirm_dialog = OUIAButton('btn-modal-confirm')
    cancel_dialog = OUIAButton('btn-modal-cancel')


class CreateCapsuleView(BaseLoggedInView):
    """Class that describes the Create Capsule page"""

    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[contains(@href, "smart_proxies")]')

    @View.nested
    class capsule(SatTab):
        name = TextInput(locator='//input[@id="smart_proxy_name"]')
        url = TextInput(locator='//input[@id="smart_proxy_url"]')
        acs_http_proxy = FilteredDropdown(id='s2id_smart_proxy_http_proxy_id')
        remove_proxy_selection = Text(locator='//*[@id="s2id_smart_proxy_http_proxy_id"]/a/abbr')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-smart_proxy_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-smart_proxy_organization_ids')

    @property
    def is_displayed(self):
        return self.submit.is_displayed


class EditCapsuleView(CreateCapsuleView):
    @View.nested
    class capsule(SatTab):
        name = TextInput(locator='//input[@id="smart_proxy_name"]')
        url = TextInput(locator='//input[@id="smart_proxy_url"]')
        download_policy = FilteredDropdown(id='s2id_smart_proxy_download_policy')
        acs_http_proxy = FilteredDropdown(id='s2id_smart_proxy_http_proxy_id')
        remove_proxy_selection = Text(locator='//*[@id="s2id_smart_proxy_http_proxy_id"]/a/abbr')

    @View.nested
    class lifecycle_enviroments(SatTab):
        TAB_NAME = 'Lifecycle Environments'
        resources = MultiSelect(id='ms-smart_proxy_lifecycle_environment_ids')


class CapsuleDetailsView(BaseLoggedInView):
    """Class that describes the Capsule Details page"""

    breadcrumb = BreadCrumb()

    actions = ActionsDropdown('./div[a[contains(@data-toggle, "dropdown")]]')
    edit_capsule = Text('//a[normalize-space(.)="Edit"]')
    delete_capsule = Text('//a[normalize-space(.)="Delete"]')

    success_message = Text('//div[contains(@aria-label, "Success Alert")]')
    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')
    confirm_deletion = DeleteCapsuleConfirmationDialog()

    @View.nested
    class overview(SatTab):
        TAB_NAME = 'Overview'

        reclaim_space_button = Button('Reclaim Space')

        url = Text('.//div[preceding-sibling::div[contains(., "URL")]]')
        version = Text('.//span[@class="proxy-version"]')
        active_features = Text('.//div[contains(., "Active features")]/ancestor::div[@class="row"]')
        refresh_features = Button('Refresh features')
        hosts_managed = Text('.//div[preceding-sibling::div[contains(., "Hosts managed")]]')
        failed_fetaures_info = Text('//div[@id="failed-modules"]')
        log_messages_info = Text(
            '//a[contains(@href, "#logs") and contains(@data-toggle, "tooltip")][1]'
        )
        error_messages_info = Text(
            '//a[contains(@data-original-title, "error") or contains(@title, "error")]'
        )
        active_features_info = Text('//h2[contains(@data-toggle, "tooltip")]')

        last_sync = Text('.//div[span[contains(text(), "Last sync:")]]')
        synchronize_action_drop = ActionsDropdown(
            '//div[contains(@class, "dropdown") and .//button[normalize-space(.)="Synchronize"]]'
        )
        storage_info = Text('//div[contains(@class, "progress-bar")]/span[1]')

    @View.nested
    class services(SatTab):
        TAB_NAME = 'Services'
        container_gateway_version = Text(
            '//div[contains(., "Container_Gateway")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )

        dynflow_version = Text(
            '//div[contains(., "Dynflow")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )

        content_version = Text(
            '//div[contains(., "Content")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )
        content_supportted_content_types = Text(
            '//div[contains(., "Content")]/div[@class="col-md-8"]/ul'
        )

        registration_version = Text(
            '//div[contains(., "Registration")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )

        script_version = Text(
            '//div[contains(., "Script")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )

        templates_version = Text(
            '//div[contains(., "Templates")]/following-sibling::div[contains(., "Version")]/div[@class="col-md-8"][1]'
        )

    @View.nested
    class logs(SatTab):
        TAB_NAME = 'Logs'

        search_bar = TextInput(locator='//input[@aria-controls="table-proxy-status-logs"]')
        filter_by_level = Select(locator='//select[@id="logs-filter"]')
        refresh_button = Text(
            locator='//a[normalize-space(.)="Refresh" and contains(@data-url,"expire_logs")]'
        )

        table = SatTable(
            './/table',
            column_widgets={
                'Time': Text('./td[1]'),
                'Level': Text('./td[2]'),
                'Message': Text('./td[3]'),
            },
        )

        pagination = Pagination()

    @View.nested
    class content(SatTab):
        TAB_NAME = 'Content'

        top_content_table = ExpandableTable(
            component_id='capsule-content-table',
            column_widgets={
                0: Button(locator='./button[@aria-label="Details"]'),
                'Environment': Text('./a'),
                'Last sync': Text('./span[contains(@class, "pf-c-label ")]'),
                3: Dropdown(locator='.//div[contains(@class, "pf-c-dropdown")]'),
            },
        )

        mid_content_table = ExpandableTable(
            component_id='expandable-content-views',
            column_widgets={
                'cv_info_list': ItemsList(locator='//ul'),
            },
        )

        expanded_repo_details = ItemsList(
            locator='(//ul[@aria-label="Expanded repository details"])'
        )

        def read(self):
            """Reads content table and returns its content"""
            read_top_content = self.top_content_table.read()
            lce_names = []
            result = {}
            lce_names.extend(row['Environment'] for row in read_top_content)

            for lce in lce_names:
                self.top_content_table.row(Environment=lce)[0].click()
                mid_content_read = self.mid_content_table.read()
                cv_names = []
                cv_names.extend(row['Content view'] for row in mid_content_read)

                result[lce] = {
                    'top_row_content': self.top_content_table.row(Environment=lce).read(),
                }

                for i, cv in enumerate(cv_names):
                    self.mid_content_table.row(content_view=cv)[0].click()
                    self.expanded_repo_details.locator += f'[{i+1}]'
                    result[lce][cv] = {
                        'mid_row_content': self.mid_content_table.row(content_view=cv).read(),
                        'expanded_repo_details': [
                            col.split('\n') for col in self.expanded_repo_details.read()
                        ],
                    }
                    self.expanded_repo_details.locator = '['.join(
                        self.expanded_repo_details.locator.split('[')[:-1]
                    )

                    self.mid_content_table.row(content_view=cv)[0].click()

                self.top_content_table.row(Environment=lce)[0].click()

            return result


class CapsulesView(BaseLoggedInView, SearchableViewMixinPF4):
    """Class that describes the Capsule Details page"""

    title = Text('//h1[normalize-space(.)="Capsules"]')
    create_capsule = Text('//a[contains(@class, "btn")][contains(@href, "smart_proxies/new")]')
    documentation = Text('//a[contains(@class, "btn")][contains(@href, "manual")]')
    success_message = Text('//div[contains(@aria-label, "Success Alert")]')
    error_message = Text('//div[contains(@aria-label, "Danger Alert")]')
    confirm_deletion = DeleteCapsuleConfirmationDialog()

    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a[contains(@href, "smart_proxies")]'),
            'Locations': Text('./td[3]'),
            'Organizations': Text('./td[4]'),
            'Features': Text('./td[4]'),
            'Status': Text('./td[5]'),
            'Actions': ActionsDropdown('./div[contains(@class, "btn-group")]'),
        },
    )

    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None
