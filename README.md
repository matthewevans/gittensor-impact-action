# Gittensor Impact Action

Generate a README-ready SVG card that shows the share of repository velocity
attributed to Gittensor contributors.

The action reads merged PR attribution from the public Gittensor API, compares it
with repository Git history, renders dark and light SVG cards, and publishes the
cards to either stable GitHub release assets or a dedicated assets branch.
Generated images do not need to be committed to the target repository's default
branch.

## Example

<p align="center">
  <a href="https://gittensor.io/miners/repository?name=phase-rs%2Fphase">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/phase-rs/phase/gittensor-impact-assets/gittensor-impact-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/phase-rs/phase/gittensor-impact-assets/gittensor-impact-light.svg">
      <img src="https://raw.githubusercontent.com/phase-rs/phase/gittensor-impact-assets/gittensor-impact-light.svg" alt="Gittensor contributor impact for phase.rs" width="600">
    </picture>
  </a>
</p>

## Usage

Create `.github/workflows/gittensor-impact.yml` in the repository you want to
track:

```yaml
name: Gittensor Impact

on:
  schedule:
    - cron: "0 14 * * 1"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: matthewevans/gittensor-impact-action@v1
        with:
          accent-color: "#ff6a00"
          neutral-color: "#85898b"
```

Run the workflow once, then add this to your README:

```html
<p align="center">
  <a href="https://gittensor.io/miners/repository?name=OWNER%2FREPO">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/OWNER/REPO/releases/download/gittensor-impact/gittensor-impact-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/OWNER/REPO/releases/download/gittensor-impact/gittensor-impact-light.svg">
      <img src="https://github.com/OWNER/REPO/releases/download/gittensor-impact/gittensor-impact-light.svg" alt="Gittensor contributor impact" width="600">
    </picture>
  </a>
</p>
```

Replace `OWNER` and `REPO` with your repository owner and name.

If the repository has immutable releases enabled, publish to a dedicated assets
branch instead:

```yaml
- uses: matthewevans/gittensor-impact-action@v1
  with:
    publish-mode: branch
    asset-branch: gittensor-impact-assets
```

Branch-mode README URLs use `raw.githubusercontent.com`:

```html
<p align="center">
  <a href="https://gittensor.io/miners/repository?name=OWNER%2FREPO">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/OWNER/REPO/gittensor-impact-assets/gittensor-impact-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/OWNER/REPO/gittensor-impact-assets/gittensor-impact-light.svg">
      <img src="https://raw.githubusercontent.com/OWNER/REPO/gittensor-impact-assets/gittensor-impact-light.svg" alt="Gittensor contributor impact" width="600">
    </picture>
  </a>
</p>
```

## Inputs

| Input | Default | Description |
| --- | --- | --- |
| `repo` | workflow repository | GitHub repository in `owner/name` form. |
| `since` | `30 days ago` | Git date window for the report. |
| `until` | empty | Optional Git date window end. |
| `ref` | `HEAD` | Git ref to analyze. |
| `release-tag` | `gittensor-impact` | Stable release tag that stores generated SVG assets. |
| `publish-mode` | `release` | `release` or `branch`. |
| `asset-branch` | `gittensor-impact-assets` | Branch used when `publish-mode` is `branch`. |
| `title` | repo-specific default | Optional card title. |
| `subtitle` | built-in default | Optional card subtitle. |
| `accent-color` | `#ff6a00` | Primary color for Gittensor contribution data. |
| `accent-alt-color` | accent color | Secondary accent color for labels. |
| `neutral-color` | `#85898b` | Comparator color for non-Gittensor data. |
| `neutral-text-color` | neutral color | Optional text color for non-Gittensor labels. |
| `dark-background` | theme default | Optional dark theme background color. |
| `light-background` | theme default | Optional light theme background color. |
| `gittensor-api-url` | `https://api.gittensor.io/prs` | Public Gittensor PR API URL. |
| `pr-limit` | `6000` | Maximum merged PRs to fetch from GitHub. |
| `github-token` | `github.token` | Token with `contents: write` permission for release assets. |

## Outputs

| Output | Description |
| --- | --- |
| `dark-svg-url` | Public release asset URL for the dark SVG. |
| `light-svg-url` | Public release asset URL for the light SVG. |
| `readme-html` | HTML snippet for embedding the generated card. |

## Attribution Model

The action classifies merged PRs by PR number:

- PR present in the Gittensor API for the repository: Gittensor.
- GitHub bot author: excluded from the comparison.
- Everything else: non-Gittensor.

This avoids trusting commit author names or emails for paid contributor
attribution. Direct pushes are treated as non-Gittensor by default.

## Notes

The target workflow must use a full clone. This action performs checkout with
`fetch-depth: 0` internally because shallow clones can misattribute the
graft-boundary commit as a large artificial change.
