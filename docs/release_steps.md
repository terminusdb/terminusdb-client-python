# Release Steps

## Quick Release

1. Update release notes (`RELEASE_NOTES.md`)
2. Bump version (`bumpversion [patch|minor|major]`) and push `main` with the bump commit
3. Create a GitHub Release with a `vX.Y.Z` tag — publishing it triggers the release workflow, which verifies the tag matches `pyproject.toml` and deploys to PyPI

### Bump version (updates files + creates tag)

To not create a tag, use `--no-tag`.

```bash
bumpversion [patch|minor|major]
```

### Create the release (triggers automated PyPI deployment)

Draft a GitHub Release at https://github.com/terminusdb/terminusdb-client-python/releases/new with a new `vX.Y.Z` tag matching the bumped version, then publish it. The `release.yml` workflow checks that the tag equals `pyproject.toml`'s version and fails otherwise.

**Monitor**: https://github.com/terminusdb/terminusdb-client-python/actions

## Details

### What bumpversion updates
- `terminusdb_client/__version__.py`
- `pyproject.toml`
- `.bumpversion.cfg`

### Automated deployment
Publishing a GitHub Release triggers `.github/workflows/release.yml` to:
- Verify the release tag matches `pyproject.toml`'s version
- Build with Poetry
- Publish to PyPI as `terminusdb` via trusted publishing (`id-token`)

PyPI trusted publishing must be registered for the `release.yml` workflow file in the `terminusdb` project settings on PyPI.

### Manual deployment (if needed)
```bash
poetry build
poetry publish
```

### Troubleshooting

**Version conflicts:** Never delete published PyPI versions. Create a new patch release instead.

## Prerequisites

- Install: `pip install bumpversion`
- PyPI publishing uses trusted publishing (OIDC) — no API token secret needed
