---
name: yc
description: Search and query the Y Combinator (YC) company directory. Use when the user asks about YC startups, batches, industries, or wants to find companies in the YC ecosystem.
---

# YC Company Directory

You have access to the `yc` CLI tool for querying the Y Combinator company directory (~5,700+ companies).

## Prerequisites

If `yc` is not installed, install it:
```bash
pip install git+https://github.com/dattran2346/yc-cli.git
```

## Commands

### Search companies
```bash
yc search "<query>"                          # full-text search
yc search "ai" --batch "Winter 2025"         # search + filter
yc search "fintech" --hiring --limit 10      # hiring fintech companies
```

### List companies with filters
```bash
yc list --batch "Winter 2025"                # by batch
yc list --industry "Fintech" --status Active # by industry + status
yc list --top --sort team_size --limit 10    # top companies by size
yc list --hiring --limit 50                  # all hiring companies
```

### Get company details
```bash
yc info <slug>                               # e.g. yc info airbnb
```

### Browse metadata
```bash
yc batches                                   # list all YC batches
yc industries                                # list all industries
yc tags                                      # list all tags
yc stats                                     # summary statistics
```

## Output format

- Default output is **JSON** with an envelope: `{"count": N, "total": T, "offset": O, "companies": [...]}`
- Use `--format table` for human-readable output
- Use `--fields name,website,one_liner` to select specific fields
- Use `--limit` and `--offset` for pagination

## Available filters

| Flag | Description | Example |
|------|-------------|---------|
| `--batch` | Exact batch match (case-insensitive) | `--batch "Winter 2025"` |
| `--industry` | Industry substring match | `--industry fintech` |
| `--status` | Company status | `--status Active` (Active/Inactive/Acquired/Public) |
| `--tag` | Tag substring match | `--tag marketplace` |
| `--hiring/--no-hiring` | Hiring status | `--hiring` |
| `--top` | Only top companies (list only) | `--top` |
| `--sort` | Sort by name/batch/team_size (list only) | `--sort team_size` |
| `--limit` | Max results (default 20) | `--limit 50` |
| `--offset` | Skip N results | `--offset 20` |
| `--fields` | Comma-separated field names | `--fields name,website` |

## Default summary fields

List and search commands return these fields by default: `name`, `slug`, `one_liner`, `batch`, `status`, `industry`, `team_size`, `isHiring`, `website`.

Use `yc info <slug>` for all fields including `long_description`, `all_locations`, `tags`, `regions`, `founders`, etc.

## Tips

- Results are cached locally for 24h. Use `--no-cache` to force refresh.
- Use `yc cache-clear` to clear all cached data.
- Combine search + filters: `yc search "api" --industry B2B --hiring --limit 30`
- For large result sets, paginate: first `--limit 20`, then `--limit 20 --offset 20`, etc.
