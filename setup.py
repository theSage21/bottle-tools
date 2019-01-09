import os
from setuptools import setup

__version__ = "0.40"

# we want the path relative to this script since when sphinx will read this
# file to access version number we don't want problems
readme = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")
with open(readme, "r") as fl:
    long_desc = fl.read()


setup(
    name="bottle_tools",
    author="Arjoonn Sharma",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version=__version__,
    packages=["bottle_tools"],
    install_requires=["bottle"],
    python_requires=">=3.6",
    project_urls={"Source": "https://github.com/thesage21/bottle_tools"},
    zip_safe=False,
)
