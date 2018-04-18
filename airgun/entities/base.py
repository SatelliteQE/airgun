import attr


@attr.s
class BaseEntity(object):
    browser = attr.ib()

    @property
    def session(self):
        return self.browser.extra_objects['session']

    @property  # could be cached
    def navigate_to(self):
            return self.session.navigator.navigate
