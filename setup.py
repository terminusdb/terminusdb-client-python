# read the contents of your README file
import re
from os import path

import setuptools

# Add README.md in PyPI project description, reletive links are changes to obsolute

page_target = "https://github.com/terminusdb/terminusdb-client-python/blob/master/"
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

matched = re.finditer(r"\]\(\S+\)", long_description)
replace_pairs = {}
for item in matched:
    if item.group(0)[2:10] != "https://" and item.group(0)[2:9] != "http://":
        replace_pairs[item.group(0)] = (
            item.group(0)[:2] + page_target + item.group(0)[2:]
        )
for old_str, new_str in replace_pairs.items():
    long_description = long_description.replace(old_str, new_str)

# ---

requires = ["requests", "numpydoc", "click<8.0,>=7.0", "shed", "typeguard", "tqdm"]

extras_require = {"dataframe": ["numpy >= 1.13.0", "pandas >= 0.23.0"]}

setuptools.setup(
    name="terminusdb-client",
    version="10.0.17",
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
    extras_require=extras_require,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "terminusdb = terminusdb_client.scripts.scripts:terminusdb",
        ],
    },
)
