# Contributing to Terminus Client Python

Thanks for interested to contribute to Terminus Client Python, to get started, fork this repo and follow the [instruction setting up dev environment](#setting-up-dev-environment). If you don't have idea where to start, you can look for [`good first issue`](https://github.com/terminusdb/terminus-client-python/contribute) or `help wanted` label at issues. All pull request should follow the [Pull Request Format Guideline](#pull-request-format-guideline) and pull request (PR) that involving coding should come with [tests](#writing-tests-and-testing) and [documentations](#writing-documentation). **All pull request should be made towards `dev` branch**

## Setting up dev environment

Make sure you have Python>=3.6 installed. We use [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) for dev environment, to install pipenv:

`pip3 install pipenv --upgrade`

[Fork and clone](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) this repo, then in your local repo:

`pipenv install --dev`

To “editable” install the local Terminus Client Python:

`pip3 install -e .`

## Writing tests and testing

We are using [`pytest`](https://docs.pytest.org/en/latest/) for testing. All tests are stored in `/tests`

To run the tests:

`pytest /tests`

## Writing Documentation

Please follow [numpydoc docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html) for documentation. It is important to follow the formatting as all documentation will be automatically rendered using [Sphinx](https://www.sphinx-doc.org/).

## Pull Request Format Guideline

Please put the type of the pull request in the title:

* [Doc] for documentation
* [Bug] for bug fixes
* [Feature] for new features
* [WIP] for work in progress (will not be reviewed)

Also, if there is a related issues, please also put the issue numbers in blankets in the title, for example: (#10)

It will be great to describe what you have done in the pull request (more detail the better). If there is a issue that can be closed by this PR, you can put `Close #XX` or `Fix #XX` (while XX is the issue number) to close that issue automatically when your PR is merged.

Following the guideline makes the reviewing process of the PR much efficient.
