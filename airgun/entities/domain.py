from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.domain import (DomainCreateView, DomainEditView,
                                 DomainListView)


class DomainEntity(BaseEntity):
    _DEFAULT_ORG = 'Default Organization'
    _DEFAULT_LOC = 'Default Location'
    _CREATE_SUCCESSFUL = 'Successfully created {}.'
    _UPDATE_SUCCESSFUL = 'Successfully updated {}.'
    _DELETE_SUCCESSFUL = 'Successfully deleted {}.'

    @staticmethod
    def _submit_domain_form(view, **kwargs):
        """Create or update domain.

        Form is the same for both cases, we use 1 method here to fill the form.
        """
        dns_domain = kwargs.get('dns_domain')
        full_name = kwargs.get('full_name')
        dns_capsule = kwargs.get('dns_capsule')
        parameters = kwargs.get('parameters')
        locations = kwargs.get('locations')
        organizations = kwargs.get('organizations')

        # Fill 'Domain' tab
        if dns_domain:
            view.domain.dns_domain.fill(dns_domain)
        if full_name:
            view.domain.full_name.fill(full_name)
        if dns_capsule:
            view.domain.dns_capsule.fill(dns_capsule)

        # Fill 'Parameters' tab
        if parameters:
            params = []
            for param_name, param_value in parameters.items():
                params.append({'name': param_name, 'value': param_value})
            view.parameters.params.fill(params)  # fill overwrites old params

        # Fill locations tab
        if locations:
            view.locations.multiselect.set_assigned(locations)

        # Fill organizations tab
        if organizations:
            view.organizations.multiselect.set_assigned(organizations)

        view.submit_button.click()

    def create(self, dns_domain, **kwargs):
        """
        Create a new domain.

        :param dns_domain: str, full DNS domain name
        :param full_name: (optional) str, full name describing the domain
        :param dns_capsule: (optional) str of DNS capsule to use
        :param parameters: (optional) param dict or list of param dicts to set
            Format: [{'name': str, 'value': str}]
        :param locations: list of location strings to be assigned.
            All other locations will be unassigned.
            Default: ['Default Location']
        :param organizations: list of org strings to be assigned.
            All other orgs will be unassigned.
            Default: ['Default Organization']
        """
        view = self.navigate_to(self, 'New')

        kwargs['dns_domain'] = dns_domain

        if not kwargs.get('locations'):
            kwargs['locations'] = [self._DEFAULT_LOC]
        if not kwargs.get('organizations'):
            kwargs['organizations'] = [self._DEFAULT_ORG]

        self._submit_domain_form(view, **kwargs)

        wait_for(
            lambda: view.flash.messages, fail_condition=[], timeout=10,
            delay=2, message='wait for flash success'
        )
        view.flash.assert_success_message(self._CREATE_SUCCESSFUL.format(dns_domain))

    def search(self, value=None):
        """Search for 'value' and return domain names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        view.search(value or '')
        return [row['Description'].text for row in view.table.rows()]

    def read(self, domain_name):
        """Return dict with properties of domain."""
        view = self.navigate_to(self, 'Edit', entity_name=domain_name)
        properties = dict(
            dns_domain=view.domain.dns_domain.read(),
            full_name=view.domain.full_name.read(),
            dns_capsule=view.domain.dns_capsule.read(),
            parameters=view.parameters.params.read(),
            locations=view.locations.multiselect.read()['assigned'],
            organizations=view.organizations.multiselect.read()['assigned']
        )
        # Return only non-null entries
        return {key: val for key, val in properties.items() if val}

    def update(self, domain_name, **kwargs):
        """
        Update an existing domain.

        Only the kwargs which are passed in will be modified. You must modify
        at least one value.

        :param domain_name: name of domain to update
        :param dns_domain: (optional) str, full DNS domain name
        :param full_name: (optional) str, full name describing the domain
        :param dns_capsule: (optional) str of DNS capsule name
        :param parameters: (optional) param dict or list of param dicts to set
            Format: [{'name': str, 'value': str}]
            Existing params are overwritten.
        :param locations: (optional) list of location strings to be assigned.
            All other locations will be unassigned.
        :param organizations: (optional) list of org strings to be assigned.
            All other orgs will be unassigned.
        """
        if not kwargs:
            raise ValueError('no kwargs given for edit()')

        view = self.navigate_to(self, 'Edit', entity_name=domain_name)
        self._submit_domain_form(view, **kwargs)
        wait_for(
            lambda: view.flash.messages, fail_condition=[], timeout=10,
            delay=2, message='wait for flash success'
        )

        # If domain is renamed, flash message contains the new name...
        updated_name = kwargs.get('dns_domain') or domain_name
        view.flash.assert_success_message(
            self._UPDATE_SUCCESSFUL.format(updated_name))

    def delete(self, name):
        view = self.navigate_to(self, 'All')
        self.search(name)
        row = view.table.row(('Description', name))
        row['Actions'].widget.click()
        self.browser.handle_alert()
        wait_for(
            lambda: view.flash.messages, fail_condition=[], timeout=10,
            delay=2, message='wait for flash success'
        )
        view.flash.assert_success_message(self._DELETE_SUCCESSFUL.format(name))


@navigator.register(DomainEntity, 'All')
class DomainList(NavigateStep):
    VIEW = DomainListView

    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'Domains')


@navigator.register(DomainEntity, 'New')
class AddNewDomain(NavigateStep):
    VIEW = DomainCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.create_button.click()


@navigator.register(DomainEntity, 'Edit')
class EditDomain(NavigateStep):
    VIEW = DomainEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        row = self.parent.table.row(('Description', entity_name))
        row['Description'].widget.click()
