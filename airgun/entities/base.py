

class BaseEntity(object):

    def __init__(self, browser, session):
        self.browser = browser
        self.session = session
        self.navigate_to = session.navigator.navigate
