import bottle
import pytest
from bottle_tools import add_cors, fill_args


@pytest.fixture
def app():
    yield bottle.Bottle()


def test_cors_gets_added(app):
    @app.get("/")
    def some_fn():
        return "x"

    n_routes = len(app.routes)
    app = add_cors(app)
    n_new_routes = len(app.routes)
    assert n_routes < n_new_routes


def test_cors_adds_only_one_rule_for_multiple_methods(app):
    @app.get("/some")
    def some_fn():
        return "x"

    @app.post("/some")
    def some_fn2():
        return "x"

    n_routes = len(app.routes)
    app = add_cors(app)
    n_new_routes = len(app.routes)
    assert n_routes < n_new_routes
    assert n_new_routes - n_routes == 1
