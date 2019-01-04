import inspect
from functools import wraps, partial


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
    """
    if function is None:
        return partial(fill_args, json_only=json_only)
    spec = inspect.getargspec(function)
    # figure out which args have defaults supplied
    args, defaults = spec.args, spec.defaults
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
                return abort(400, f"Please provide `{name}`")
            val = given.get(name)
            if val is not None:
                kwargs[name] = val
        return function(**kwargs)

    return new_fn
