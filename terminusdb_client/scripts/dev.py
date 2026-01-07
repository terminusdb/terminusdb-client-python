#!/usr/bin/env python3
"""
Development scripts for TerminusDB Python Client.
These scripts provide centralized development commands through Poetry.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

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
    """Format code with shed."""
    print("Formatting code...")
    run_command(["poetry", "run", "shed"])


def lint():
    """Run linting checks (read-only)."""
    print("Running linting checks...")

    # Check code formatting with shed
    print("Checking code formatting with shed...")
    temp_dir = Path("/tmp/terminusdb-lint-check")
    temp_dir.mkdir(exist_ok=True)

    try:
        # Copy code to temp directory
        src_dir = Path("terminusdb_client")
        if src_dir.exists():
            shutil.copytree(src_dir, temp_dir / src_dir.name, dirs_exist_ok=True)

        # Initialize git repo in temp directory if not exists
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=temp_dir, capture_output=True)

        # Run shed in temp directory
        subprocess.run(
            ["poetry", "run", "shed"],
            cwd=temp_dir,
            capture_output=True
        )

        # Check if any files were modified
        git_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )

        if git_result.returncode != 0 or git_result.stdout.strip():
            print("❌ Code formatting issues found. Run 'poetry run dev lint-fix' to fix.")
            sys.exit(1)
        else:
            print("✅ Code formatting is correct.")
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Run flake8
    print("Running flake8...")
    run_command(["poetry", "run", "flake8", "terminusdb_client"])


def flake8():
    """Run flake8 linting only."""
    print("Running flake8...")
    run_command(["poetry", "run", "flake8", "terminusdb_client"])


def lint_fix():
    """Run linting and fix issues automatically."""
    print("Running linting fixes...")

    # Format code with shed
    print("Fixing code formatting with shed...")
    run_command(["poetry", "run", "shed"])

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

    # 2. Format
    format()

    # 3. Lint
    lint()

    # 4. Run all tests
    test_all()

    print("\nAll PR preparation checks completed successfully!")
    print("\nSummary of checks performed:")
    print("  ✓ Code formatted with shed")
    print("  ✓ Linting passed (flake8, shed check)")
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
        print("  format        - Format code with shed")
        print("  lint          - Run linting checks (read-only)")
        print("  lint-fix      - Run linting and fix issues automatically")
        print("  flake8        - Run flake8 linting only")
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
        print("  format        - Format code with shed")
        print("  lint          - Run linting checks (read-only)")
        print("  lint-fix      - Run linting and fix issues automatically")
        print("  flake8        - Run flake8 linting only")
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
