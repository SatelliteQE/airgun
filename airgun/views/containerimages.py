from widgetastic.widget import Text, View
from widgetastic_patternfly5 import Button as PF5Button
from widgetastic_patternfly5.ouia import (
    Button as PF5OUIAButton,
    PatternflyTable as PF5OUIATable,
    Text as PF5OUIAText,
    Title as PF5OUIATitle,
)

from airgun.views.common import BaseLoggedInView, PF4Search
from airgun.widgets import CompoundExpandableTable  # Import the new widget
from airgun.views.all_hosts import MenuToggleDropdownInTable

class SyncedContainerPullablePath(View):
    """Represents the Synced Container pullable paths table"""
    table = PF5OUIATable(
        component_id='manifest-repositories-table',
        column_widgets={
            'Environment': Text('.//td[1]'),
            'Content view': Text('.//td[2]'),
            'Repository': Text('.//td[3]'),
            'Pullable path': Text('.//td[4]'),
        },
    )

class ContainerImagesView(BaseLoggedInView):
    title = PF5OUIATitle('container-images-title')
    searchbox = PF4Search()

    # Passing in the nested table as content_view, refer to ExpandableTable docs for info
    table = CompoundExpandableTable(
        locator='.//table[@data-ouia-component-id="synced-container-images-table"]',
        column_widgets={
            'Tag': Text('./a'),
            'Manifest digest': Text('./a'),
            'Type': Text('./a'),
            'Product': Text('./a'),
            'Labels | Annotations': Text('./a'),
            6: MenuToggleDropdownInTable()
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class ManifestDetailsView(View):
    """Details page for a specific manifest"""

    title = PF5OUIATitle('manifest-details-title')

    pullable_paths_expand = PF5Button(locator=".//button[@class='pf-v5-c-expandable-section__toggle']")
    pullable_paths = SyncedContainerPullablePath()

    manifest_name = PF5OUIAText('manifest-name-value')
    manifest_repository = PF5OUIAText('manifest-repository-value')
    manifest_digest = Text(
        './/h6[@data-ouia-component-id="manifest-digest-label"]/following-sibling::div/span[1]'
    )
    manifest_created = Text(
        './/h6[@data-ouia-component-id="manifest-creation-label"]/following-sibling::span[1]'
    )
    manifest_modified = Text(
        './/h6[@data-ouia-component-id="manifest-modified-label"]/following-sibling::span[1]'
    )
    manifest_type = Text('.//p[@data-ouia-component-id="manifest-type-value"]')
    manifest_labels = Text(
        './/h6[@data-ouia-component-id="manifest-labels-label"]/following-sibling::div[1]'
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed

class ManifestPullablePathsModal(View):
    """Labels and Annotations Modal for synced container images"""

    ROOT = './/div[@data-ouia-component-id="pullable-paths-modal"]'

    pullable_paths = SyncedContainerPullablePath()

    close_button = PF5OUIAButton('pullable-paths-close-button')




class ManifestLabelAnnotationModal(View):
    """Labels and Annotations Modal for synced container images"""

    ROOT = './/div[@data-ouia-component-id="labels-annotations-modal"]'

    title = PF5OUIATitle('.//h1')

    confirm = PF5OUIAButton('labels-annotations-close-button')
    sha_hash = PF5OUIAText('.//p/strong')
