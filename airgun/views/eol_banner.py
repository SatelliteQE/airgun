from widgetastic.widget import ClickableMixin, Text, View


class EOLBannerView(View, ClickableMixin):
    name = Text('//div[@id="satellite-eol-banner"]')
    dismiss_button = Text('//*[@id="satellite-oel-banner-dismiss-button"]')

    @property
    def warning(self):
        """Return whether the banner is displayed in warning style"""
        return 'warning' in " ".join(self.browser.classes(self.name))

    @property
    def danger(self):
        """Return whether the banner is displayed in danger style"""
        return 'danger' in " ".join(self.browser.classes(self.name))

    @property
    def is_displayed(self):
        return self.name.is_displayed
