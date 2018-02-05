

class BaseEntity(object):

    def __init__(self, browser):
        self.browser = browser
        self.session = browser.extra_objects['session']
        self.navigate_to = self.session.navigator.navigate
