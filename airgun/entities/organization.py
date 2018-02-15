from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.common import BaseLoggedInView


class OrganizationEntity(BaseEntity):
    def select(self, org_name):
        self.navigate_to(self, 'Context', org_name=org_name)


@navigator.register(OrganizationEntity, 'Context')
class SelectOrganizationContext(NavigateStep):
    VIEW = BaseLoggedInView

    def am_i_here(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        current_org = self.view.taxonomies.current_org()
        if len(org_name) > 30:
            org_name = org_name[:27] + '...'
        return current_org == org_name

    def step(self, *args, **kwargs):
        org_name = kwargs.get('org_name')
        if not org_name:
            raise ValueError('Specify proper value for org_name parameter')
        self.view.taxonomies.select_org(org_name)
