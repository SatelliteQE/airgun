from airgun.exceptions import InsightsOrganizationPageError
from airgun.navigation import NavigateStep
from airgun.views.rhai import InsightsOrganizationErrorView


class InsightsNavigateStep(NavigateStep):

    def post_navigate(self, _tries, *args, **kwargs):
        """raise Error if Organization Error page is displayed"""
        org_err_page_view = InsightsOrganizationErrorView(self.view.browser)
        if org_err_page_view.is_displayed:
            raise InsightsOrganizationPageError(org_err_page_view.read())
