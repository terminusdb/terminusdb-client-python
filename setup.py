import setuptools

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requires = [
   'requests'
]

test_requirements = [
    'pytest>=3',
    'pytest-cov',
    'pytest-mock',
    'pytest-xdist',
]

setuptools.setup(
    name="terminus-client-python",
    version="0.0.4",
    author="TerminusDB group",
    author_email="terminusdatabase@gmail.com",
    description="Python client for Terminus DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={'': ['LICENSE']},
    url="https://github.com/terminusdb/terminus-client-python",
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requires,

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=test_requirements,
    python_requires='>=3.6',
)
