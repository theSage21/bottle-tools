import bottle
import inspect
from collections import defaultdict
from functools import wraps, partial

__version__ = "2019.1.16"


def __cors_dict__(allow_credentials, origin, methods):
    cors_string = "Origin, Accept , Content-Type"
    cors_string += ", X-Requested-With, X-CSRF-Token"
    CORS_HEADERS = {
        "Access-Control-Allow-Headers": cors_string,
        "Access-Control-Allow-Origin": origin,
    }
    if methods is not None:
        CORS_HEADERS["Access-Control-Allow-Methods"] = methods
    if allow_credentials is not None:
        value = "true" if allow_credentials else "false"
        CORS_HEADERS.update({"Access-Control-Allow-Credentials": value})
    return CORS_HEADERS


def __make_cors_fn__(rule, routes, allow_credentials, origin):
    methods = ", ".join([r.method for r in routes])

    def fn():
        final_origin = (
            bottle.request.headers.get("Origin") if origin is None else origin
        )
        headers = __cors_dict__(allow_credentials, final_origin, methods)
        bottle.response.headers.update(headers)

    return fn


def add_cors(app, allow_credentials=True, origin=None):
    """

    Automatically adds CORS routes to an app instance. This function must be
    called after **ALL** routes have been registered to the app. This does not add
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

    @app.hook("after_request")
    def add_cors_headers():
        final_origin = (
            bottle.request.headers.get("Origin") if origin is None else origin
        )
        headers = __cors_dict__(allow_credentials, final_origin, None)
        bottle.response.headers.update(headers)

    return app


def fill_args(function=None, *, json_only=False):
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
                    return bottle.abort(415, 'please use "application/json"')
                given = bottle.request.forms
        elif method == "GET":
            given = bottle.request.query
        else:  # Everyone else uses forms
            given = bottle.request.forms
        if given is None:
            return bottle.abort(
                400,
                "Cannot detect arguments. GET: query, POST: json/form body, Others: form body",
            )
        kwargs = dict()
        for name in spec.args:
            if name not in given and name not in defaults:
                return bottle.abort(400, "Please provide `{name}`".format(name=name))
            if name in given:
                val = given[name]
                if name in anno and not isinstance(val, anno[name]):
                    return bottle.abort(
                        400,
                        "Please provide `{name}: {type}`".format(
                            name=name, type=anno[name]
                        ),
                    )
                kwargs[name] = val
        return function(**kwargs)

    return new_fn


def prefix_docs(app):
    """
    Automatically prefixes docstrings of functions with the method and route in
    the decorator. Use this just like `add_cors` but **BEFORE** you register any
    routes. For example

    .. code:: python

        app = bottle.Bottle()
        app = prefix_docs(app)

        @app.get('/some')
        def my_fn():
            "This function returns some"
            return 'some'

    When this code is used in Sphinx or via `help(my_fn)`, the docstring being processed is the following

    ::

        **GET** */some*

        This function returns some

    This information changes as per the code. So if you register more than one
    url to the same function, it will reflect that in the code.

    .. code:: python

        @app.get('/search')
        @app.get('/🔎')
        def my_search():
            "Perform some fancy search"
            return 'found it!'

    The docstring looks like:

    ::

        **GET** */some*
        **GET** */🔎*

        Perform some fancy search

    """

    def _prefix_docs(method):
        @wraps(method)  # method liket post/get/delete etc
        def new_api_registration(route, *a, **kw):
            # method is called with a route and returns a decorator
            fn_decorator = method(route, *a, **kw)

            # we build a new decorator which will add the docstrings
            @wraps(fn_decorator)
            def new_decorator(*args, **kwargs):
                fn = fn_decorator(*args, **kwargs)
                doc = "**{}** *{}*".format(method.__name__.upper(), route)
                doc += "" if fn.__doc__ is None else "\n\n{}".format(fn.__doc__)
                fn.__doc__ = doc
                return fn

            return new_decorator

        return new_api_registration

    app.post = _prefix_docs(app.post)
    app.get = _prefix_docs(app.get)
    app.delete = _prefix_docs(app.delete)
    app.put = _prefix_docs(app.put)
    return app
