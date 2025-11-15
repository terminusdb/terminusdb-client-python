# Release Steps

## Quick Release

1. Update release notes (`RELEASE_NOTES.md`)
2. Bump version (bumpversion [patch|minor|major])
3. Push new tag (`git push origin main --tags`)

### Bump version (updates files + creates tag)

To not create a tag, use `--no-tag`.

```bash
bumpversion [patch|minor|major]
```

### Create and push tag (triggers automated PyPI deployment)

```bash
git push origin main --tags
```

**Monitor**: https://github.com/terminusdb/terminusdb-client-python/actions

## Details

### Create tag manually

```bash
git tag -s v11.1.0 -m "Release v11.1.0"
git push origin main --tags
```

### What bumpversion updates
- `terminusdb_client/__version__.py`
- `pyproject.toml`
- `.bumpversion.cfg`

### Automated deployment
Pushing a tag triggers GitHub Actions to:
- Run tests (Python 3.9-3.12)
- Build with Poetry
- Publish to PyPI

### Manual deployment (if needed)
```bash
poetry build
poetry publish
```

### Troubleshooting

**Version conflicts:** Never delete published PyPI versions. Create a new patch release instead.

## Prerequisites

- Install: `pip install bumpversion`
- PyPI publishing handled via `PYPI_API_TOKEN` secret in GitHub Actions
