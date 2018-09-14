from widgetastic.widget import (
    Text,
    TextInput,
    View,
    Checkbox,
)
from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
    SatTab,
)
from airgun.widgets import (
    FilteredDropdown,
    ActionsDropdown,
    SatTable,
    MultiSelect,
)
from widgetastic_patternfly import BreadCrumb


class ContainerView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Containers']")
    new = Text("//a[contains(@href, '/containers/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Status': Text("./span[text()='On']"),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ContainerCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Steps'
            and self.breadcrumb.read() == 'Create container'
        )

    @View.nested
    class preliminary(BaseLoggedInView):
        next_step = Text("//button[contains(@id, 'next')]")

        @View.nested
        class compute_resource(SatTab):
            TAB_NAME = 'Compute resource'
            first_part = "s2id_docker_container_wizard_states_"
            second_part = "preliminary_compute_resource_id"
            id_of_element = first_part + second_part
            deploy_on = FilteredDropdown(id=id_of_element)

        @View.nested
        class locations(SatTab):
            first_part = "ms-docker_container_wizard_states_"
            second_part = "preliminary_location_ids"
            id_of_element = first_part + second_part
            resources = MultiSelect(id=id_of_element)

        @View.nested
        class organizations(SatTab):
            first_part = "ms-docker_container_wizard_states_"
            second_part = "preliminary_organization_ids"
            id_of_element = first_part + second_part
            resources = MultiSelect(id=id_of_element)

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class image(BaseLoggedInView):
        next_step = Text("//button[contains(@id, 'next')]")

        @View.nested
        class content_view(SatTab):
            TAB_NAME = 'Content View'
            lifecycle_environment = FilteredDropdown(
                id='s2id_kt_environment_id')
            content_view = FilteredDropdown(id='s2id_content_view_id')
            repository = FilteredDropdown(id='s2id_repository_id')
            tag = FilteredDropdown(id='s2id_tag_id')
            capsule = FilteredDropdown(id='s2id_capsule_id')

        @View.nested
        class docker_hub(SatTab):
            TAB_NAME = 'Docker hub'
            search = TextInput(
                id='hub_docker_container_wizard_states_image_repository_name')
            tag = TextInput(
                id='hub_docker_container_wizard_states_image_tag')
            search_for_images = Text(
                "./a[contains(@id,'search_repository_button_hub')]")

        @View.nested
        class external_registry(SatTab):
            TAB_NAME = 'External registry'
            registry = FilteredDropdown(
                id='s2id_docker_container_wizard_states_image_registry_id')
            search = TextInput(
                id='hub_docker_container_wizard_states_image_repository_name')
            tag = TextInput(
                id='hub_docker_container_wizard_states_image_tag')
            search_for_images = Text(
                "./a[contains(@id,'search_repository_button_registry')]")

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class configuration(BaseLoggedInView):
        next_step = Text("//button[contains(@id, 'next')]")
        name = TextInput(
            id='docker_container_wizard_states_configuration_name')
        command = TextInput(
            id='docker_container_wizard_states_configuration_command')
        entrypoint = TextInput(
            id='docker_container_wizard_states_configuration_entrypoint')
        cpu_sets = TextInput(
            id='docker_container_wizard_states_configuration_cpu_set')
        cpu_shares = TextInput(
            id='docker_container_wizard_states_configuration_cpu_shares')
        memory = TextInput(
            id='docker_container_wizard_states_configuration_memory')

        def after_fill(self, was_change):
            self.next_step.click()

    @View.nested
    class environment(BaseLoggedInView):
        add_environment_variable = Text(
            "//a[text()='Add environment variable']")
        add_exposed_port = Text("//a[text()='Add Exposed Port']")
        add_dns = Text("//a[text()='Add DNS']")
        tty = Checkbox(id='docker_container_wizard_states_environment_tty')
        attach_stdin = Checkbox(
            id='docker_container_wizard_states_environment_attach_stdin')
        attach_stdout = Checkbox(
            id='docker_container_wizard_states_environment_attach_stdout')
        attach_stderr = Checkbox(
            id='docker_container_wizard_states_environment_attach_stderr')
        submit = Text("//button[contains(@id, 'next')]")
