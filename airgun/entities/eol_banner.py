from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.views.eol_banner import EOLBannerView


class EOLBannerEntity(BaseEntity):
    def read(self):
        view = self.navigate_to(self, 'NavigateToEOLBanner')
        return view.read()

    def dismiss(self):
        view = self.navigate_to(self, 'NavigateToEOLBanner')
        view.dismiss_button.click()

    def is_warning(self):
        view = self.navigate_to(self, 'NavigateToEOLBanner')
        return view.warning

    def is_danger(self):
        view = self.navigate_to(self, 'NavigateToEOLBanner')
        return view.danger


@navigator.register(EOLBannerEntity)
class NavigateToEOLBanner(NavigateStep):
    VIEW = EOLBannerView

    def step(self, *args, **kwargs):
        self.view.wait_displayed()

    def am_i_here(self, *args, **kwargs):
        return self.view.is_displayed
