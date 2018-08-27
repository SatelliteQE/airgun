from nailgun import entities, config
from airgun.base.application.implementations import AirgunImplementationContext, Implementation


class RESTAPI(Implementation):
    """REST API implementation using nailgun"""

    register_method_for = AirgunImplementationContext.external_for
    name = "RESTAPI"
    entities = entities
    config = config
