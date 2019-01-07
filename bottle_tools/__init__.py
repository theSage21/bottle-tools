import bottle
import inspect
from collections import defaultdict
from functools import wraps, partial

__version__ = "0.34"


def __cors_dict__(allow_credentials, origin, methods):
    cors_string = "Origin, Accept , Content-Type"
    cors_string += ", X-Requested-With, X-CSRF-Token"
    CORS_HEADERS = {
        "Access-Control-Allow-Methods": methods,
        "Access-Control-Allow-Headers": cors_string,
        "Access-Control-Allow-Origin": origin,
    }
    if allow_credentials is not None:
        value = "true" if allow_credentials else "false"
        CORS_HEADERS.update({"Access-Control-Allow-Credentials": value})
    return CORS_HEADERS


def __make_cors_fn__(rule, routes, allow_credentials, origin):
    methods = ", ".join([r.method for r in routes])

    def fn():
        origin = bottle.request.headers.get("Origin") if origin is None else origin
        headers = __cors_dict__(allow_credentials, origin, methods)
        bottle.response.update(headers)

    return fn


def add_cors(app, allow_credentials=True, origin=None):
    """

    Automatically adds CORS routes to an app instance. This function must be
    called after ALL routes have been registered to the app. This does not add
    OPTIONS to those routes which already have an OPTIONS method registered.

    .. code:: python

        # add your routes however you want
        # in the END, add the next line
        app = add_cors(app)
        # then continue to run your app or whatever you wanted to do
        app.run()
    """
    # collect methods and other info
    grp_by_rule = defaultdict(list)
    for route in app.routes:
        grp_by_rule[route.rule].append(route)
    # add the new routes
    cors_functions = []
    for rule, routes in grp_by_rule.items():
        if not any([r.method == "OPTIONS" for r in routes]):
            fn = __make_cors_fn__(rule, routes, allow_credentials, origin)
            app.route(rule, method=["OPTIONS"])(fn)
    return app


def fill_args(function=None, *, json_only=True):
    """
    Use to populate function arguments from json/query string/post data provided in API call.

    If supplied, the json_only argument ensures that a POST api call only ever works under
    the content_type of `application/json`.


    Some example usages:

    .. code:: python

        @app.post('/user')
        @fill_args
        def change_user_data(name, age):
            # Do something with name and age

        @app.post('/user')
        @fill_args(json_only=True)
        def change_user_data(name, age):
            # Do something with name and age

        @app.get('/search')
        @fill_args
        def search_for_string(query):
            # Do something with query

    If you provide simple type annotations the decorator will ensure those types. For example

    .. code:: python

        @app.post('/calculate')
        @fill_args
        def fancy_calculation(a: int, b: float):
            return {'result': a + b}

    This bit of code raises an error if `a` is not supplied as an integer or if
    `b` is not given as a float. Complex types like those described in the
    `Typing module <https://docs.python.org/3/library/typing.html>`_ in Python
    docs are not yet supported. If you would like them to be added, please open
    up an issue.
    """
    if function is None:
        return partial(fill_args, json_only=json_only)
    spec = inspect.getfullargspec(function)
    # figure out which args have defaults supplied
    args, defaults, anno = spec.args, spec.defaults, spec.annotations
    defaults = (
        set()
        if defaults is None
        else set([name for _, name in zip(reversed(defaults), reversed(args))])
    )

    @wraps(function)
    def new_fn():
        method = bottle.request.method  # Current request being processed
        if method == "POST":
            given = bottle.request.json
            if given is None:
                if json_only:
                    return abort(415, 'please use "application/json"')
                given = bottle.request.forms
        elif method == "GET":
            given = bottle.request.query
        else:  # Everyone else uses forms
            given = bottle.request.forms
        if given is None:
            return abort(
                400,
                "Cannot detect arguments. GET: query, POST: json/form body, Others: form body",
            )
        kwargs = dict()
        for name in spec.args:
            if name not in given and name not in defaults:
                return abort(400, "Please provide `{name}`".format(name=name))
            val = given.get(name)
            if name in anno and not isinstance(given.get(name), anno[name]):
                return abort(
                    400,
                    "Please provide `{name}: {type}`".format(
                        name=name, type=anno[name]
                    ),
                )
            kwargs[name] = val
        return function(**kwargs)

    return new_fn
