#!/usr/bin/env python3
"""
Development scripts for TerminusDB Python Client.
These scripts provide centralized development commands through Poetry.
"""

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Constants
PYTHON_CLIENT_DIR = "terminusdb_client/"
RUNNING_FLAKE8_MSG = "Running flake8..."
RUNNING_RUFF_MSG = "Running ruff..."
RUFF_WARNING_MSG = "⚠️  Ruff found some issues it couldn't fix automatically:\n   Run 'poetry run dev ruff' to see all issues"
# Constants for pytest arguments
PYTEST_TB_SHORT = "--tb=short"
PYTEST_COV = "--cov=terminusdb_client"
PYTEST_COV_TERM = "--cov-report=term-missing"
PYTEST_COV_XML = "--cov-report=xml:cov.xml"


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check)


def init():
    """Initialize development environment."""
    print("Initializing development environment...")

    # Install/upgrade pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Install Poetry if not present
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        run_command([sys.executable, "-m", "pip", "install", "poetry"])

    # Install dependencies
    run_command(["poetry", "install", "--with", "dev"])

    # Install pre-commit hooks
    run_command(["poetry", "run", "pre-commit", "install"])

    print("\n Development environment initialized successfully!")
    print("   Use 'poetry run <command>' to run development commands.")
    print(
        "   Available commands: init-dev, install-dev, format, lint, check, test, test-unit, test-integration, test-all, docs, clean, pr"
    )


def install():
    """Install package in editable mode."""
    print("Installing package in editable mode...")
    run_command([sys.executable, "-m", "pip", "install", "-e", "."])


def format():
    """Format code with black and ruff (no auto-commits)."""
    print("Formatting code...")
    # Find all Python files and format them
    python_files = glob.glob("terminusdb_client/**/*.py", recursive=True)
    if python_files:
        # Run black for formatting
        print("Running black...")
        run_command(["poetry", "run", "black"] + python_files)
        # Run ruff for import sorting and other fixes (ignore unfixed errors)
        print(RUNNING_RUFF_MSG)
        try:
            run_command(["poetry", "run", "ruff", "check", "--fix", PYTHON_CLIENT_DIR])
        except subprocess.CalledProcessError:
            print(RUFF_WARNING_MSG)
    else:
        print("No Python files found to format.")


def lint():
    """Run linting checks (read-only)."""
    print("Running linting checks...")

    # Run flake8
    print(RUNNING_FLAKE8_MSG)
    run_command(["poetry", "run", "flake8", "terminusdb_client"])


def flake8():
    """Run flake8 linting only."""
    print(RUNNING_FLAKE8_MSG)
    run_command(["poetry", "run", "flake8", "terminusdb_client"])


def ruff():
    """Run ruff linting only."""
    print(RUNNING_RUFF_MSG)
    run_command(["poetry", "run", "ruff", "check", PYTHON_CLIENT_DIR])


def lint_fix():
    """Run linting and fix issues automatically."""
    print("Running linting fixes...")

    # Format code with black and ruff
    print("Fixing code formatting...")
    python_files = glob.glob("terminusdb_client/**/*.py", recursive=True)
    if python_files:
        # Run black for formatting
        print("Running black...")
        run_command(["poetry", "run", "black"] + python_files)
        # Run ruff for import sorting and other fixes
        print(RUNNING_RUFF_MSG)
        try:
            run_command(["poetry", "run", "ruff", "check", "--fix", PYTHON_CLIENT_DIR])
        except subprocess.CalledProcessError:
            print(RUFF_WARNING_MSG)
    else:
        print("No Python files found to format.")

    print("✅ Linting fixes completed!")
    print("Note: Some issues (like flake8 violations) may need manual fixes.")


def check():
    """Run all static analysis checks."""
    print("Running static analysis checks...")
    lint()


def test():
    """Run unit tests (alias for test-unit)."""
    test_unit()


def test_unit():
    """Run unit tests only."""
    print("Running unit tests...")
    run_command(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "pytest",
            "terminusdb_client/tests/",
            "--ignore=terminusdb_client/tests/integration_tests/",
            PYTEST_TB_SHORT,
            PYTEST_COV,
            PYTEST_COV_TERM,
        ]
    )


def test_integration():
    """Run integration tests (requires Docker)."""
    print("Running integration tests...")
    run_command(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "pytest",
            "terminusdb_client/tests/integration_tests/",
            PYTEST_TB_SHORT,
            PYTEST_COV,
            PYTEST_COV_TERM,
        ]
    )


def test_all():
    """Run all tests (unit + integration)."""
    print("Running all tests...")
    run_command(
        [
            "poetry",
            "run",
            "python",
            "-m",
            "pytest",
            "terminusdb_client/tests/",
            PYTEST_TB_SHORT,
            PYTEST_COV,
            PYTEST_COV_TERM,
            PYTEST_COV_XML,
        ]
    )


def docs():
    """Build documentation."""
    print("Building documentation...")
    os.chdir("docs")
    try:
        run_command(["make", "html"])
    finally:
        os.chdir("..")


def tox():
    """Run tox for isolated testing."""
    print("Running tox...")
    run_command(["poetry", "run", "tox"])


def clean():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")

    # Directories to remove
    dirs_to_clean = [
        ".coverage",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        "build/",
        "dist/",
        "*.egg-info/",
    ]

    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"Removed file: {path}")

    # Remove __pycache__ directories
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)

    # Remove .pyc files
    for pyc in Path(".").rglob("*.pyc"):
        pyc.unlink()


def pr():
    """Run all PR preparation checks."""
    print("Running PR preparation checks...")

    # 1. Clean
    clean()

    # 2. Check formatting (don't fix)
    print("\nChecking code formatting...")
    try:
        run_command(["poetry", "run", "black", "--check", "--diff", "terminusdb_client/"])
        print("✅ Black formatting is correct.")
    except subprocess.CalledProcessError:
        print("❌ Black formatting issues found.")
        print("   Run 'poetry run dev format' to fix formatting issues")
        sys.exit(1)

    # 3. Lint
    lint()
    
    # 4. Check ruff for any remaining issues
    print("\nChecking for ruff issues...")
    try:
        run_command(["poetry", "run", "ruff", "check", PYTHON_CLIENT_DIR])
        print("✅ No ruff issues found.")
    except subprocess.CalledProcessError:
        print("❌ Ruff issues found. Please fix them manually.")
        print("   Run 'poetry run dev ruff' to see all issues")
        sys.exit(1)

    # 5. Run all tests
    test_all()

    print("\nAll PR preparation checks completed successfully!")
    print("\nSummary of checks performed:")
    print("  ✓ Code formatting is correct (black, ruff)")
    print("  ✓ Linting passed (flake8, ruff check)")
    print("  ✓ All tests passed (unit + integration)")
    print("  ✓ Coverage report generated")
    print("\nYour PR is ready for submission!")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("TerminusDB Python Client Development Scripts")
        print("\nUsage: poetry run dev <command>")
        print("\nAvailable commands:")
        print("  init-dev      - Initialize development environment")
        print("  install-dev   - Install package in editable mode")
        print("  format        - Format code with black and ruff")
        print("  lint          - Run flake8 linting (read-only)")
        print("  lint-fix      - Run linting and fix issues automatically")
        print("  flake8        - Run flake8 linting only")
        print("  ruff          - Run ruff linting only")
        print("  check         - Run all static analysis checks")
        print("  test          - Run unit tests")
        print("  test-unit     - Run unit tests only")
        print("  test-integration - Run integration tests")
        print("  test-all      - Run all tests (unit + integration)")
        print("  docs          - Build documentation")
        print("  tox           - Run tox for isolated testing")
        print("  clean         - Clean build artifacts")
        print("  pr            - Run all PR preparation checks")
        sys.exit(0)

    command = sys.argv[1]

    if command in ["-h", "--help", "help"]:
        print("TerminusDB Python Client Development Scripts")
        print("\nUsage: poetry run dev <command>")
        print("\nAvailable commands:")
        print("  init-dev      - Initialize development environment")
        print("  install-dev   - Install package in editable mode")
        print("  format        - Format code with black and ruff")
        print("  lint          - Run flake8 linting (read-only)")
        print("  lint-fix      - Run linting and fix issues automatically")
        print("  flake8        - Run flake8 linting only")
        print("  ruff          - Run ruff linting only")
        print("  check         - Run all static analysis checks")
        print("  test          - Run unit tests")
        print("  test-unit     - Run unit tests only")
        print("  test-integration - Run integration tests")
        print("  test-all      - Run all tests (unit + integration)")
        print("  docs          - Build documentation")
        print("  tox           - Run tox for isolated testing")
        print("  clean         - Clean build artifacts")
        print("  pr            - Run all PR preparation checks")
        sys.exit(0)

    command_map = {
        "init": init,
        "init-dev": init,
        "install": install,
        "install-dev": install,
        "format": format,
        "lint": lint,
        "lint-fix": lint_fix,
        "flake8": flake8,
        "ruff": ruff,
        "check": check,
        "test": test,
        "test-unit": test_unit,
        "test-integration": test_integration,
        "test-all": test_all,
        "docs": docs,
        "tox": tox,
        "clean": clean,
        "pr": pr,
    }

    if command not in command_map:
        print(f"Unknown command: {command}")
        print("Run 'poetry run dev --help' to see available commands.")
        sys.exit(1)

    # Execute the command
    command_map[command]()


if __name__ == "__main__":
    main()
