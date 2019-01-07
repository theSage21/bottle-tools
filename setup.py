from setuptools import setup


with open("README.md", "r") as fl:
    long_desc = fl.read()


setup(
    name="bottle_tools",
    author="Arjoonn Sharma",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    version="0.31",
    packages=["bottle_tools"],
    install_requires=["bottle"],
    python_requires=">=3.6",
    project_urls={"Source": "https://github.com/thesage21/bottle_tools"},
    zip_safe=False,
)
