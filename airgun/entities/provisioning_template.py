from airgun.navigation import navigator
from airgun.entities.template import (
        TemplateEntity,
        ShowAllTemplates,
        AddNewTemplate,
        EditTemplate,
        CloneTemplate,
)
from airgun.views.provisioning_template import (
    ProvisioningTemplateCreateView,
    ProvisioningTemplateDetailsView,
    ProvisioningTemplatesView,
)


class ProvisioningTemplateEntity(TemplateEntity):
    pass


@navigator.register(ProvisioningTemplateEntity, 'All')
class ShowAllProvisioningTemplates(ShowAllTemplates):
    VIEW = ProvisioningTemplatesView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Provisioning Templates')


@navigator.register(ProvisioningTemplateEntity, 'New')
class AddNewProvisioningTemplate(AddNewTemplate):
    VIEW = ProvisioningTemplateCreateView


@navigator.register(ProvisioningTemplateEntity, 'Edit')
class EditProvisioningTemplate(EditTemplate):
    VIEW = ProvisioningTemplateDetailsView


@navigator.register(ProvisioningTemplateEntity, 'Clone')
class CloneProvisioningTemplate(CloneTemplate):
    VIEW = ProvisioningTemplateCreateView
