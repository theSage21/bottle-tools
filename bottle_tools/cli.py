import os
import argparse


def get_parser():
    parser = argparse.ArgumentParser(prog="python -m bottle_tools")
    parser.add_argument(
        "-t",
        "--template",
        default=False,
        action="store_true",
        help="""Add a standard django like folder/file layout""",
    )
    return parser


def main(parser):
    args = parser.parse_args()

    if args.template:
        name = input("Name of folder: ")
        os.mkdir(name)
        os.mkdir(os.path.join(name, "apps"))
        with open(os.path.join(name, "apps", "__init__.py"), "w") as fl:
            fl.write("")
        with open(os.path.join(name, "apps", "example.py"), "w") as fl:
            fl.write(
                f"""
    from {name} import app

    @app.get('/home')
    def fn():
        return 'hi'
    """
            )
        with open(os.path.join(name, "__init__.py"), "w") as fl:
            fl.write(
                """
    import bottle
    import bottle_tools as bt

    app = bottle.Bottle()
    app = bt.prefix_docs(app)"""
            )

        with open(os.path.join(name, "__main__.py"), "w") as fl:
            fl.write(
                f"""
    from {name}.apps import example
    # add other apps here
    from {name} import app

    import bottle_tools as bt
    app = bt.add_cors(app)

    app.run()
            """
            )
    else:
        print(parser.print_help())
