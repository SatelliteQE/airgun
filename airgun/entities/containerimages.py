from navmazing import NavigateToSibling
from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.containerimages import (
    ContainerImagesView,
    ManifestDetailsView,
    ManifestPullablePathsModal,
)


class ContainerImagesEntity(BaseEntity):
    endpoint_path = '/labs/container_images'

    def read_pullable_paths(self, manifest_tag, manifest_digest):
        """Read synced container list pullable paths info from the modal and the main details page,
            only returning the info if both are the same

        Args:
            manifest_tag: Tag of the manifest list
            manifest_digest: Digest of the specific manifest
        """
        # Read pullable paths information from the Synced Containers table
        view = self.navigate_to(self, 'Synced')
        view.searchbox.search(f'tag = {manifest_tag}')
        view.title.click()
        view.table[0][6].widget.item_select('View pullable paths')
        pullable_modal = ManifestPullablePathsModal(self.browser)
        if pullable_modal.is_displayed:
            manifest_table_pullable_paths = pullable_modal.read()['pullable_paths']['table'][0]
            pullable_modal.close_button.click()
        else:
            raise NoSuchElementException('Pullable Paths Modal was not displayed.')
        # Read pullable paths information from the Manifest Details page
        view = self.navigate_to(
            self,
            'ManifestDetails',
            manifest_tag=manifest_tag,
            manifest_digest=manifest_digest,
            is_child=False,
        )
        view.pullable_paths_expand.click()
        manifest_details_pullable_paths = view.read()['pullable_paths']['table'][0]
        if manifest_table_pullable_paths == manifest_details_pullable_paths:
            return manifest_details_pullable_paths
        else:
            raise Exception('Pullable paths information between table and details did not match.')

    def read_manifest_details(self, manifest_tag, manifest_digest, is_child=False):
        """Read synced container manifest details

        Args:
            manifest_tag: Tag of the manifest list
            manifest_digest: Digest of the specific manifest
            is_child: Is the manifest a child manifest, or a manifest list
        """
        view = self.navigate_to(
            self,
            'ManifestDetails',
            manifest_tag=manifest_tag,
            manifest_digest=manifest_digest,
            is_child=is_child,
        )
        return view.read()

    def read_synced_table(self, manifest_tag=None, expand=True):
        """Read synced container images table, optionally reading expandable rows and searching on manifest digest or tag

        Args:
            manifest_tag: Tag of the manifest list
            expand: Whether to expand table rows or not
        """
        view = self.navigate_to(self, 'Synced')
        if manifest_tag:
            view.searchbox.search(f'tag = {manifest_tag}')
            view.parent.title.click()
        if expand:
            return view.table.read(expand)
        return view.table.read()


@navigator.register(ContainerImagesEntity, 'Synced')
class SyncedContainersTab(NavigateStep):
    """Navigate to Container Images tab."""

    VIEW = ContainerImagesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Lab Features', 'Container Images')


@navigator.register(ContainerImagesEntity, 'ManifestDetails')
class ShowManifestDetails(NavigateStep):
    """Navigate to Manifest Details page by filtering by manifest list tag, and then clicking the specific
        manifest digest in the table.

    Args:
        manifest_tag: Tag of the manifest list
        manifest_digest: Digest of the specific manifest
        is_child: Is the manifest a child manifest, or a list
    """

    VIEW = ManifestDetailsView

    prerequisite = NavigateToSibling('Synced')

    def am_i_here(self, *args, **kwargs):
        manifest_digest = kwargs.get('manifest_digest')
        return self.view.manifest_digest == manifest_digest

    def step(self, *args, **kwargs):
        manifest_tag = kwargs.get('manifest_tag')
        manifest_digest = kwargs.get('manifest_digest')
        is_child = kwargs.get('is_child')
        self.parent.searchbox.search(f'tag = {manifest_tag}')
        self.parent.title.click()
        if is_child:
            self.parent.table.row(tag=manifest_tag).expand()
            self.parent.browser.element(
                f'.//td[@data-label="Manifest digest"]/a[text()="{manifest_digest}"]'
            ).click()
        else:
            self.parent.table.row(manifest_digest=manifest_digest)['Manifest digest'].click()
