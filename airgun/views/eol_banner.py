from widgetastic.widget import ClickableMixin, Text, View


class EOLBannerView(View, ClickableMixin):
    name = Text('//div[@id="satellite-eol-banner"]')
    dismiss_button = Text('//*[@id="satellite-oel-banner-dismiss-button"]')
    LIFECYCLE_LINK = '//a[text()[normalize-space(.) = "Red Hat Satellite Product Life Cycle"]]'
    HELPER_LINK = '//a[text()[normalize-space(.) = "Red Hat Satellite Upgrade Helper."]]'

    @property
    def warning(self):
        """Return whether the banner is displayed in warning style"""
        return 'warning' in " ".join(self.browser.classes(self.name))

    @property
    def danger(self):
        """Return whether the banner is displayed in danger style"""
        return 'danger' in " ".join(self.browser.classes(self.name))

    @property
    def lifecycle_link(self):
        """Return the result link element of this row"""
        return self.browser.element(self.LIFECYCLE_LINK)

    @property
    def helper_link(self):
        """Return the result link element of this row"""
        return self.browser.element(self.HELPER_LINK)

    @property
    def is_displayed(self):
        return self.name.is_displayed
