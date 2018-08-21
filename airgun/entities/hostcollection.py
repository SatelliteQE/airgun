from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.hostcollection import (
    HostCollectionCreateView,
    HostCollectionEditView,
    HostCollectionsView,
    HostCollectionChangeAssignedContentView,
    HostCollectionInstallErrataView,
    HostCollectionManagePackagesView,
    HostCollectionActionTaskDetailsView,
)


class HostCollectionEntity(BaseEntity):

    def create(self, values):
        view = self.navigate_to(self, 'New')
        view.fill(values)
        view.submit.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.actions.fill('Remove')
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read()

    def update(self, entity_name, values):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.details.fill(values)

    def associate_host(self, entity_name, host_name):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.hosts.resources.add(host_name)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def manage_packages(
            self, entity_name, content_type='Package', packages=None,
            action='install', action_via='via Katello Agent'):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.manage_packages.click()
        view = HostCollectionManagePackagesView(view.browser)
        if content_type is not None:
            view.content_type.fill(content_type)
        if packages is not None:
            view.packages.fill(packages)
        view.apply_action(action, action_via=action_via)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def install_errata(self, entity_name, errata_id,
                       install_via='via Katello agent'):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.install_errata.click()
        view = HostCollectionInstallErrataView(view.browser)
        view.search.fill(errata_id)
        view.table.row(Id=errata_id)[0].widget.fill(True)
        if install_via:
            view.install.select(install_via)
        else:
            view.install.click()
            view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()
        task_view = HostCollectionActionTaskDetailsView(view.browser)
        task_view.progressbar.wait_for_result()
        return task_view.read()

    def change_assigned_content(self, entity_name, lce, content_view):
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.details.change_assigned_content.click()
        view = HostCollectionChangeAssignedContentView(view.browser)
        view.lce.fill({lce: True})
        view.content_view.fill(content_view)
        view.assign.click()
        view.dialog.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()
        task_view = HostCollectionActionTaskDetailsView(view.browser)
        task_view.progressbar.wait_for_result()
        return task_view.read()


@navigator.register(HostCollectionEntity, 'All')
class ShowAllHostCollections(NavigateStep):
    VIEW = HostCollectionsView

    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'Host Collections')


@navigator.register(HostCollectionEntity, 'New')
class AddNewHostCollections(NavigateStep):
    VIEW = HostCollectionCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HostCollectionEntity, 'Edit')
class EditHostCollections(NavigateStep):
    VIEW = HostCollectionEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()
