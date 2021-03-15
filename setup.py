# read the contents of your README file
from os import path

import setuptools

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requires = ["requests"]

test_requirements = [
    "pytest>=3",
    "pytest-cov",
    "pytest-mock",
    "pytest-xdist",
    "pytest-runner",
]

extras_require = {"dataframe": ["numpy >= 1.13.0", "pandas >= 0.23.0"]}

setuptools.setup(
    name="terminusdb-client",
    version="0.6.1",
    author="TerminusDB group",
    author_email="terminusdatabase@gmail.com",
    description="Python client for Terminus DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={"": ["LICENSE"]},
    url="https://github.com/terminusdb/terminusdb-client-python",
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["pytest-runner"],
    tests_require=test_requirements,
    extras_require=extras_require,
    python_requires=">=3.6",
)
