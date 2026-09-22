# Releasing FastWER

Releases are built from a version tag and uploaded by GitHub Actions using
PyPI Trusted Publishing. The tag must match the value in `VERSION` with a `v`
prefix.

## One-time PyPI configuration

In the `fastwer` project's PyPI publishing settings, add a GitHub Trusted
Publisher with these values:

- Owner: `kahne`
- Repository: `fastwer`
- Workflow: `release.yml`
- Environment: `pypi`

Create a GitHub environment named `pypi` and configure a required reviewer.
Protect tags matching `v*` so only maintainers can create or update them.

## Release checklist

1. Update `VERSION` and add a dated section to `CHANGELOG.md`.
2. Open a release-preparation pull request. Confirm the Python tests, full
   wheel build/test matrix, and distribution metadata validation pass, then
   merge it. Pull requests build artifacts without publishing them.
3. Create and push the matching tag, for example:

   ```bash
   git switch master
   git pull --ff-only
   git tag -s v0.2.0 -m "fastwer 0.2.0"
   git push origin v0.2.0
   ```

4. Approve the `pypi` environment deployment when GitHub requests it.
5. Verify the files and metadata on PyPI, then create GitHub release notes for
   the same tag from the matching changelog section.
