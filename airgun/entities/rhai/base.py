from airgun.exceptions import DestinationNotReachedError
from airgun.navigation import NavigateStep
from airgun.views.rhai import InsightsOrganizationErrorView


class InsightsOrganizationPageError(Exception):
    """Raised when navigating to insight plugin pages and the organization is not selected
    or the current selected organization has no manifest.
    """


class InsightsNavigateStep(NavigateStep):
    def post_navigate(self, _tries, *args, **kwargs):
        """Raise Error if Destination view is not displayed or Organization Error page
        is displayed.
        """
        if not self.view.is_displayed:
            org_err_page_view = InsightsOrganizationErrorView(self.view.browser)
            if org_err_page_view.is_displayed:
                raise InsightsOrganizationPageError(org_err_page_view.read())
            raise DestinationNotReachedError(
                f'Navigation destination view "{self.view.__class__.__name__}" not reached'
            )
