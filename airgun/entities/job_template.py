from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.job_template import JobTemplateCreateView
from airgun.views.job_template import JobTemplateEditView
from airgun.views.job_template import JobTemplatesView


class JobTemplateEntity(BaseEntity):
    endpoint_path = '/job_templates'

    def create(self, values):
        """Create new job template"""
        view = self.navigate_to(self, 'New')
        wait_for(
            lambda: JobTemplateCreateView(self.browser).is_displayed is True,
            timeout=60,
            delay=1,
        )
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for specific job template"""
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, editor_view_option=None, widget_names=None):
        """Read Job template values from job template Edit view.

        :param entity_name: Job template name
        :param editor_view_option: The edit view option to set.
        :param widget_names: Read only the widgets in widget_names (Optional)
        """
        view = self.navigate_to(
            self, 'Read', entity_name=entity_name, editor_view_option=editor_view_option
        )
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update necessary values for existing job template"""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def clone(self, entity_name, values):
        """Clone existing job template"""
        view = self.navigate_to(self, 'Clone', entity_name=entity_name)
        view.fill(values)
        view.submit.click()

    def delete(self, entity_name):
        """Delete job template"""
        view = self.navigate_to(self, 'All')
        view.search(f'name="{entity_name}"')
        view.table.row(name=entity_name)['Actions'].widget.fill('Delete')
        self.browser.handle_alert()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(JobTemplateEntity, 'All')
class ShowAllTemplates(NavigateStep):
    """Navigate to All Job Templates screen."""

    VIEW = JobTemplatesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Templates', 'Job templates')


@navigator.register(JobTemplateEntity, 'New')
class AddNewTemplate(NavigateStep):
    """Navigate to Create new Job Template screen."""

    VIEW = JobTemplateCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(JobTemplateEntity, 'Edit')
class EditTemplate(NavigateStep):
    """Navigate to Edit Job Template screen.

    Args:
       entity_name: name of job template
    """

    VIEW = JobTemplateEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(f'name="{entity_name}"')
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(JobTemplateEntity, 'Read')
class ReadTemplate(EditTemplate):
    """Navigate to Read Job Template screen.

    Args:
       entity_name: name of job template
       editor_view_option: The edit view option to set.
    """

    def post_navigate(self, _tries, *args, **kwargs):
        editor_view_option = kwargs.get('editor_view_option')
        if editor_view_option is not None:
            self.view.template.template_editor.rendering_options.fill(editor_view_option)


@navigator.register(JobTemplateEntity, 'Clone')
class CloneTemplate(NavigateStep):
    """Navigate to Clone Job Template screen.

    Args:
       entity_name: name of job template to be cloned
    """

    VIEW = JobTemplateCreateView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(f'name="{entity_name}"')
        self.parent.table.row(name=entity_name)['Actions'].widget.fill('Clone')
