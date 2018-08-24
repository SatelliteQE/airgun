import sentaku


class AirgunImplementationContext(sentaku.ImplementationContext):
    """A context for Sentaku"""
    pass


class Implementation(object):

    navigator = None
    name = None

    def __init__(self, owner):
        self.owner = owner

    def __str__(self):
        return self.name

    @property
    def application(self):
        return self.owner
