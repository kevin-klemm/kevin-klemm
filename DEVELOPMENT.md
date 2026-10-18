# Development

`README.md` is shown on the GitHub profile page. Everything above the
`<!-- skills:start -->` marker is written by hand. The skills table between the
markers, and every file in `icons/`, is generated from `skills.toml`.

## Changing the skills table

1. Edit `skills.toml`: add, remove or reorder skills. Each group starts a new
   row, and rows wrap at `layout.columns`.
2. Regenerate the table and icons:

   ```sh
   uv run python -m readme_gen
   ```

3. Commit `skills.toml`, `README.md` and `icons/` together.

## Icon sources

Every icon is a 256x256 rounded tile, so the table looks consistent:

| `kind` | Source | How it is drawn |
|---|---|---|
| `skill-icons` | [tandpfun/skill-icons](https://github.com/tandpfun/skill-icons), pinned commit | Used as-is |
| `simple-icons` | [Simple Icons](https://simpleicons.org), pinned npm version | Glyph centred on a `#242938` tile in the brand colour, lightened to at least 4.5:1 contrast |
| `aws-icons` | [aws-icons](https://www.npmjs.com/package/aws-icons) (AWS Architecture Icons), pinned npm version | Scaled to the tile and clipped to its rounded corners |
| `monogram` | None | Short text in the given colour, for tools with no logo |

To add another source, subclass `IconSource` (or `RemoteSource` for a CDN) in
`readme_gen/sources.py` and register it in `REMOTE_SOURCES`. Nothing else needs
to change.

## Checks

```sh
uv run ruff check . && uv run ruff format --check .
uv run pytest
uv run python -m readme_gen --check   # fails if README.md or icons/ are stale
```

CI runs the same three steps on every push to `main` and on every pull request.
