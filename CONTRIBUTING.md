# Contributing to TerminusDB Client

Thanks for interested to contribute to TerminusDB Client, to get started, fork this repo and follow the [instruction setting up dev environment](#setting-up-dev-environment-). If you don't have idea where to start, you can look for [`good first issue`](https://github.com/terminusdb/terminusdb-client-python/contribute) or [`help wanted`](https://github.com/terminusdb/terminusdb-client-python/issues?q=is:open+is:issue+label:"help+wanted") label at issues. All pull request should follow the [Pull Request Format Guideline](#pull-request-format-guideline-) and pull request (PR) that involving coding should come with [tests](#writing-tests-and-testing-) and [documentations](#writing-documentation-).

## Setting up dev environment 💻

Make sure you have Python>=3.9 and <3.13 installed.

[Fork and clone](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) this repo, then set up your development environment using one of the methods below.

### Option 1: Using venv (recommended)

Create and activate a virtual environment:

```bash
# Create venv with Python 3.12 (or any version 3.9-3.12)
python3.12 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pytest for running tests
pip install pytest
```

### Option 2: Using pipenv

We also support [pipenv](https://pipenv-fork.readthedocs.io/en/latest/) for dev environment:

```bash
pip install pipenv --upgrade
pipenv install --dev --pre
```

Or simply run `make init`.

To "editable" install the local Terminus Client Python:

`pip install -e .`

### Running a local TerminusDB server

**To run integration tests, you need either Docker or a local TerminusDB server.**

For integration tests, you can either:

1. **Use Docker** (automatic): Tests will automatically start a Docker container if no server is detected
2. **Use a local server**: Start the TerminusDB test server from the main terminusdb repository:
   ```bash
   cd /path/to/terminusdb
   ./tests/terminusdb-test-server.sh start
   ```

The test configuration will automatically detect and use an available server.

We use [shed](https://pypi.org/project/shed/) to lint our code. Although you can do it manually by running `shed`, we highly recommend setting up the pre-commit hook to do the linting automatically.

To install the pre-commit hook:

`pre-commit install`

## Writing tests and testing ✅

We are using [pytest](https://docs.pytest.org/en/latest/) for testing. All tests are stored in `/tests`

We also use tox to run tests in a virtual environment, we recommend running `tox` for the first time before you make any changes. This is to initialize the tox environments (or do it separately by `tox -e deps`) and make sure all tests pass initially.

To run the unittests without integration tests:

`pytest terminusdb_client/tests/ --ignore=terminusdb_client/tests/integration_tests/`

To run all tests including integration tests:

`tox -e test`

To run all checks and auto formatting:

`tox -e check`

To run all tests and checks:

`tox`

**please make sure `tox` passes before making PR**

## Writing Documentation 📖

Please follow [numpydoc docstring guide](https://numpydoc.readthedocs.io/en/latest/format.html) for documentation. It is important to follow the formatting as all documentation will be automatically rendered using [Sphinx](https://www.sphinx-doc.org/).

To render the documentation locally (for preview before making your PR):

```
cd docs
make html
```

The built documentation will be in `/build/html/` which you can open `index.html` in your browser to check.

*now you are in docs directory, make sure you go back to the top directory of the repo if you want to commit and push*

## Pull Request Format Guideline 🏁

Please put the type of the pull request in the title:

* [Doc] for documentation
* [Bug] for bug fixes
* [Feature] for new features
* [WIP] for work in progress (will not be reviewed)

Also, if there is a related issues, please also put the issue numbers in blankets in the title, for example: (#10)

It will be great to describe what you have done in the pull request (more detail the better). If there is an issue that can be closed by this PR, you can put `Close #XX` or `Fix #XX` (while XX is the issue number) to close that issue automatically when your PR is merged.

Following the guideline makes the reviewing process of the PR much efficient.
