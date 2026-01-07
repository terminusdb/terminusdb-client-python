# Contributing to TerminusDB Client

Thanks for interested to contribute to TerminusDB Client, to get started, fork this repo and follow the [instruction setting up dev environment](#setting-up-dev-environment-). If you don't have idea where to start, you can look for [`good first issue`](https://github.com/terminusdb/terminusdb-client-python/contribute) or [`help wanted`](https://github.com/terminusdb/terminusdb-client-python/issues?q=is:open+is:issue+label:"help+wanted") label at issues. All pull request should follow the [Pull Request Format Guideline](#pull-request-format-guideline-) and pull request (PR) that involving coding should come with [tests](#writing-tests-and-testing-) and [documentations](#writing-documentation-).

## Quick Start (Python + Poetry) 🚀

If you have Python 3.9+ installed, here's the fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/terminusdb/terminusdb-client-python.git
cd terminusdb-client-python

# 2. Create and activate a virtual environment with Python 3.9+
python3.9 -m venv .venv  # or python3.10, python3.11, python3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install Poetry (if not already installed)
pip install poetry

# 4. Install dependencies and set up development environment
poetry install --with dev

# 5. Install pre-commit hooks (optional, requires Python 3.10+)
# If you have Python 3.10+, you can install pre-commit:
# poetry add --group dev pre-commit && poetry run pre-commit install

# 6. Install the package in editable mode
poetry run dev install-dev

# 7. Run tests to verify everything works
poetry run dev test

# 8. Get help with available commands
poetry run dev --help
```

**Important**: This project requires Python 3.9 or higher. If you're using Python 3.8, please upgrade to Python 3.9+ before proceeding.

That's it! You're now ready to start contributing. See [Poetry Scripts Reference](#poetry-scripts-reference-) for all available commands.

## Setting up dev environment 💻

Make sure you have Python>=3.9 installed. We use [Poetry](https://python-poetry.org/) for dependency management.

### Using Poetry (Recommended)

1. [Fork and clone](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) this repo

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install Poetry and dependencies:
   ```bash
   pip install poetry
   poetry install --with dev
   ```

4. Install the package in editable mode:
   ```bash
   poetry run dev install-dev
   ```

**To run integration tests, Docker must be installed locally.**

We use [shed](https://pypi.org/project/shed/) to lint our code. You can run it manually with `poetry run dev lint`, or set up a pre-commit hook (requires Python 3.10+):

```bash
poetry add --group dev pre-commit
poetry run pre-commit install
```

## Writing tests and testing ✅

We are using [pytest](https://docs.pytest.org/en/latest/) for testing. All tests are stored in `terminusdb_client/tests/`.

### Using Poetry Scripts (Recommended)

```bash
# Format your code
poetry run dev format

# Run linting (read-only, just checks)
poetry run dev lint

# Run flake8 only
poetry run dev flake8

# Fix linting issues automatically
poetry run dev lint-fix

# Run all tests
poetry run dev test-all

# Prepare your PR (runs format, lint, and all tests)
poetry run dev pr
```

### Using tox (Alternative)

You can also use tox to run tests in an isolated environment:

```bash
# Run all tests
tox -e test

# Run all checks and auto formatting
tox -e check

# Run everything
tox
```

**Please make sure all tests pass before making a PR.**

## Poetry Scripts Reference 📋

The project includes a `dev` script that provides the following commands:

| Command | Description |
|--------|-------------|
| `poetry run dev init-dev` | Initialize development environment |
| `poetry run dev install-dev` | Install package in editable mode |
| `poetry run dev format` | Format code with shed |
| `poetry run dev lint` | Run linting checks (read-only) |
| `poetry run dev lint-fix` | Run linting and fix issues automatically |
| `poetry run dev flake8` | Run flake8 linting only |
| `poetry run dev check` | Run all static analysis checks |
| `poetry run dev test` | Run unit tests |
| `poetry run dev test-unit` | Run unit tests with coverage |
| `poetry run dev test-integration` | Run integration tests |
| `poetry run dev test-all` | Run all tests |
| `poetry run dev docs` | Build documentation |
| `poetry run dev tox` | Run tox for isolated testing |
| `poetry run dev clean` | Clean build artifacts |
| `poetry run dev pr` | Run all PR preparation checks |

Run `poetry run dev --help` to see all available commands.

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
