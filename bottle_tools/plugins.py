import bottle
from functools import wraps


class ReqResp:
    """
    Pass Request and Response objects explicitly to the route function
    as the first two arguments.

    .. code::

        from bottle_tools.plugins import ReqResp
        app = Bottle()
        app.install(ReqResp())

        @app.get('/')
        def function(request, response):
            pass

    This will make migration easier in the future when Bottle moves to a
    similar function signature.
    """

    name = "reqresp"
    api = 2

    def __init__(self, pass_request=True, pass_response=True):
        self.pass_request = True
        self.pass_response = True
        print("init")

    def setup(self, app):
        app.config._define(
            "reqresp.pass_request",
            default=True,
            validate=bool,
            help="Pass the current request object as the first argument of the function",
        )
        app.config._define(
            "reqresp.pass_response",
            default=True,
            validate=bool,
            help="Pass the current response object as the first argument of the function after the request object",
        )

    def apply(self, callback, route):
        pre = []
        if route.config.get("reqresp.pass_request", False):
            pre += [bottle.request]
        if route.config.get("reqresp.pass_response", False):
            pre += [bottle.response]

        @wraps(callback)
        def wrapper(*args, **kwargs):
            return callback(*pre, *args, **kwargs)

        return wrapper
