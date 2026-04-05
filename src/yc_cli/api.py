from __future__ import annotations

import click
import httpx

from yc_cli import cache

BASE_URL = "https://yc-oss.github.io/api"

_companies_cache: list[dict] | None = None


def _fetch(path: str, ttl_hours: int = 24) -> dict | list:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    cached = cache.get(url, ttl_hours) if ttl_hours > 0 else None
    if cached is not None:
        return cached
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise click.ClickException(f"Failed to fetch {url}: {e}")
    data = resp.json()
    if ttl_hours > 0:
        cache.put(url, data)
    return data


def get_all_companies(ttl_hours: int = 24) -> list[dict]:
    global _companies_cache
    if _companies_cache is not None and ttl_hours > 0:
        return _companies_cache
    data = _fetch("companies/all.json", ttl_hours)
    _companies_cache = data
    return data


def get_top_companies(ttl_hours: int = 24) -> list[dict]:
    return _fetch("companies/top.json", ttl_hours)


def get_meta(ttl_hours: int = 24) -> dict:
    return _fetch("meta.json", ttl_hours)


def get_company(slug: str, ttl_hours: int = 24) -> dict | None:
    for c in get_all_companies(ttl_hours):
        if c.get("slug") == slug:
            return c
    return None


def search_companies(
    query: str, companies: list[dict] | None = None, ttl_hours: int = 24
) -> list[dict]:
    if companies is None:
        companies = get_all_companies(ttl_hours)
    q = query.lower()
    scored: list[tuple[float, dict]] = []
    for c in companies:
        score = 0.0
        name = (c.get("name") or "").lower()
        one_liner = (c.get("one_liner") or "").lower()
        desc = (c.get("long_description") or "").lower()
        tags = " ".join(c.get("tags") or []).lower()
        industry = (c.get("industry") or "").lower()
        if q in name:
            score += 3
        if q in one_liner:
            score += 2
        if q in tags or q in industry:
            score += 1
        if q in desc:
            score += 0.5
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
    return [c for _, c in scored]


def filter_companies(
    companies: list[dict],
    *,
    batch: str | None = None,
    industry: str | None = None,
    status: str | None = None,
    tag: str | None = None,
    hiring: bool | None = None,
) -> list[dict]:
    result = companies
    if batch:
        b = batch.lower()
        result = [c for c in result if (c.get("batch") or "").lower() == b]
    if industry:
        ind = industry.lower()
        result = [
            c
            for c in result
            if ind in (c.get("industry") or "").lower()
            or any(ind in i.lower() for i in (c.get("industries") or []))
        ]
    if status:
        s = status.lower()
        result = [c for c in result if (c.get("status") or "").lower() == s]
    if tag:
        t = tag.lower()
        result = [
            c
            for c in result
            if any(t in tg.lower() for tg in (c.get("tags") or []))
        ]
    if hiring is not None:
        result = [c for c in result if c.get("isHiring") == hiring]
    return result
