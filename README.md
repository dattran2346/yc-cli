# yc-cli

CLI tool to query the [Y Combinator company directory](https://www.ycombinator.com/companies) (~5,700+ companies). JSON output by default — designed for AI agents (Claude, Cursor, Codex, Gemini CLI, GitHub Copilot, and more).

## Install

### As an AI agent skill (recommended)

```bash
npx skills add dattran2346/yc-cli
```

This makes the `yc` skill available to Claude Code, Cursor, Codex, and 10+ other agents automatically.

### As a CLI tool

```bash
pip install git+https://github.com/dattran2346/yc-cli.git
```

Requires Python 3.10+.

## Usage

### Search companies

```bash
yc search "ai"                                  # full-text search
yc search "fintech" --hiring --limit 10          # hiring fintech companies
yc search "api" --industry B2B --batch "Winter 2025"
```

### List companies with filters

```bash
yc list --batch "Winter 2026"                    # by batch
yc list --industry Fintech --status Active       # by industry + status
yc list --top --sort team_size --limit 10        # top companies by size
yc list --hiring --limit 50                      # all hiring companies
```

### Get company details

```bash
yc info airbnb
yc info stripe
```

### Browse metadata

```bash
yc batches                                       # list all YC batches
yc industries                                    # list all industries
yc tags                                          # list all tags
yc stats                                         # summary statistics
```

## Output

JSON by default with a pagination envelope:

```json
{
  "count": 5,
  "total": 167,
  "offset": 0,
  "companies": [
    {
      "name": "Airbnb",
      "slug": "airbnb",
      "one_liner": "Book accommodations around the world.",
      "batch": "Winter 2009",
      "status": "Public",
      "industry": "Consumer",
      "team_size": 6132,
      "isHiring": false,
      "website": "http://airbnb.com"
    }
  ]
}
```

Use `--format table` for human-readable output:

```bash
yc search "stripe" --format table
```

## Options

| Flag | Description |
|------|-------------|
| `--format json\|table` | Output format (default: json) |
| `--batch` | Filter by batch (e.g. "Winter 2025") |
| `--industry` | Filter by industry (substring match) |
| `--status` | Filter by status (Active/Inactive/Acquired/Public) |
| `--tag` | Filter by tag (substring match) |
| `--hiring/--no-hiring` | Filter by hiring status |
| `--top` | Only top companies (list only) |
| `--sort` | Sort by name/batch/team_size (list only) |
| `--limit` | Max results (default: 20) |
| `--offset` | Skip N results for pagination |
| `--fields` | Comma-separated field names to return |
| `--no-cache` | Bypass 24h local cache |

## Why AI-agent friendly?

- **JSON by default** — no parsing needed
- **Envelope metadata** — `count`/`total`/`offset` for pagination awareness
- **Default limit of 20** — avoids flooding context windows
- **Summary fields** — concise output; use `yc info <slug>` for full details
- **No interactive prompts** — every command runs to completion
- **Errors to stderr** — stdout is always clean data

## Data source

Uses the [yc-oss](https://github.com/yc-oss/api) public API, updated daily. Responses are cached locally for 24 hours at `~/.cache/yc-cli/`.

## License

MIT
