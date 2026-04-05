from __future__ import annotations

import click

from yc_cli import api, cache, formatter


@click.group()
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format (default: json).",
)
@click.option("--no-cache", is_flag=True, help="Bypass cache for this request.")
@click.pass_context
def main(ctx: click.Context, fmt: str, no_cache: bool) -> None:
    """Query the Y Combinator company directory."""
    ctx.ensure_object(dict)
    ctx.obj["fmt"] = fmt
    ctx.obj["ttl"] = 0 if no_cache else 24


# -- shared options for search/list --

def filter_options(f):
    f = click.option("--limit", default=20, show_default=True, help="Max results.")(f)
    f = click.option("--offset", default=0, show_default=True, help="Skip N results.")(f)
    f = click.option("--fields", default=None, help="Comma-separated field names.")(f)
    f = click.option("--batch", default=None, help="Filter by batch (exact, case-insensitive).")(f)
    f = click.option("--industry", default=None, help="Filter by industry (substring).")(f)
    f = click.option("--status", default=None, type=click.Choice(["Active", "Inactive", "Acquired", "Public"], case_sensitive=False), help="Filter by status.")(f)
    f = click.option("--tag", default=None, help="Filter by tag (substring).")(f)
    f = click.option("--hiring/--no-hiring", default=None, help="Filter by hiring status.")(f)
    return f


def _parse_fields(fields: str | None) -> list[str] | None:
    if fields is None:
        return None
    return [f.strip() for f in fields.split(",") if f.strip()]


@main.command()
@click.argument("query")
@filter_options
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    limit: int,
    offset: int,
    fields: str | None,
    batch: str | None,
    industry: str | None,
    status: str | None,
    tag: str | None,
    hiring: bool | None,
) -> None:
    """Full-text search across YC companies."""
    ttl = ctx.obj["ttl"]
    results = api.search_companies(query, ttl_hours=ttl)
    results = api.filter_companies(
        results, batch=batch, industry=industry, status=status, tag=tag, hiring=hiring
    )
    formatter.output_companies(
        results, fmt=ctx.obj["fmt"], fields=_parse_fields(fields), limit=limit, offset=offset
    )


@main.command("list")
@filter_options
@click.option("--top", is_flag=True, help="Only top companies.")
@click.option(
    "--sort",
    type=click.Choice(["name", "batch", "team_size"]),
    default="name",
    show_default=True,
    help="Sort field.",
)
@click.pass_context
def list_cmd(
    ctx: click.Context,
    limit: int,
    offset: int,
    fields: str | None,
    batch: str | None,
    industry: str | None,
    status: str | None,
    tag: str | None,
    hiring: bool | None,
    top: bool,
    sort: str,
) -> None:
    """List YC companies with optional filters."""
    ttl = ctx.obj["ttl"]
    companies = api.get_top_companies(ttl) if top else api.get_all_companies(ttl)
    companies = api.filter_companies(
        companies, batch=batch, industry=industry, status=status, tag=tag, hiring=hiring
    )
    reverse = sort == "team_size"

    def _sort_key(c: dict) -> int | str:
        val = c.get(sort)
        if sort == "team_size":
            return val if isinstance(val, (int, float)) else 0
        return val if isinstance(val, str) else ""

    companies = sorted(companies, key=_sort_key, reverse=reverse)
    formatter.output_companies(
        companies, fmt=ctx.obj["fmt"], fields=_parse_fields(fields), limit=limit, offset=offset
    )


@main.command()
@click.argument("slug")
@click.pass_context
def info(ctx: click.Context, slug: str) -> None:
    """Show detailed info for a single company by slug."""
    company = api.get_company(slug, ctx.obj["ttl"])
    if company is None:
        raise click.ClickException(f"Company '{slug}' not found.")
    formatter.output_single(company, fmt=ctx.obj["fmt"])


@main.command()
@click.pass_context
def batches(ctx: click.Context) -> None:
    """List all YC batches."""
    meta = api.get_meta(ctx.obj["ttl"])
    items = meta.get("batches", [])
    formatter.output_meta_list(items, fmt=ctx.obj["fmt"], label="batches")


@main.command()
@click.pass_context
def industries(ctx: click.Context) -> None:
    """List all industries."""
    meta = api.get_meta(ctx.obj["ttl"])
    items = meta.get("industries", [])
    formatter.output_meta_list(items, fmt=ctx.obj["fmt"], label="industries")


@main.command()
@click.pass_context
def tags(ctx: click.Context) -> None:
    """List all tags."""
    meta = api.get_meta(ctx.obj["ttl"])
    items = meta.get("tags", [])
    formatter.output_meta_list(items, fmt=ctx.obj["fmt"], label="tags")


@main.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Show summary statistics of the YC directory."""
    ttl = ctx.obj["ttl"]
    meta = api.get_meta(ttl)
    companies = api.get_all_companies(ttl)
    formatter.output_stats(meta, companies, fmt=ctx.obj["fmt"])


@main.command("cache-clear")
def cache_clear() -> None:
    """Clear the local cache."""
    count = cache.clear()
    click.echo(f"Cleared {count} cached file(s).", err=True)
