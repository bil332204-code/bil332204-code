"""Fetch contribution calendar + repo stats for the profile README cards.

Writes data/contributions.json and data/repos.json.
Uses the GraphQL API when GITHUB_TOKEN is set (it is, inside Actions),
and falls back to scraping the public contributions page.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GH_USERNAME", "bil332204-code")
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DATA_DIR", ROOT / "data"))

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name description url stargazerCount forkCount pushedAt
        primaryLanguage { name color }
      }
    }
  }
}
"""


def graphql(token):
    body = json.dumps({"query": QUERY, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "readme-cards"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    user = payload["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [{"date": d["date"], "count": d["contributionCount"],
             "level": LEVELS.get(d["contributionLevel"], 0)}
            for w in cal["weeks"] for d in w["contributionDays"]]
    repos = [{"name": n["name"], "description": n["description"], "url": n["url"],
              "stars": n["stargazerCount"], "forks": n["forkCount"], "pushed_at": n["pushedAt"],
              "language": (n["primaryLanguage"] or {}).get("name"),
              "language_color": (n["primaryLanguage"] or {}).get("color")}
             for n in user["repositories"]["nodes"]]
    return days, repos


def scrape():
    req = urllib.request.Request(f"https://github.com/users/{USERNAME}/contributions",
                                 headers={"User-Agent": "readme-cards"})
    html = urllib.request.urlopen(req, timeout=30).read().decode()
    cells = {}
    for tag in re.findall(r"<td[^>]*ContributionCalendar-day[^>]*>", html):
        date = re.search(r'data-date="([\d-]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        cid = re.search(r'id="([^"]+)"', tag)
        if date and cid:
            cells[cid.group(1)] = {"date": date.group(1), "count": 0,
                                   "level": int(level.group(1)) if level else 0}
    for cid, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"\s*(\d+) contribution", text)
        if cid in cells and m:
            cells[cid]["count"] = int(m.group(1))
    days = sorted(cells.values(), key=lambda d: d["date"])
    # No counts in the markup? approximate from level so the cards still work.
    if days and not any(d["count"] for d in days):
        for d in days:
            d["count"] = d["level"]
    return days, None


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN")
    days, repos = None, None
    if token:
        try:
            days, repos = graphql(token)
        except Exception as e:  # noqa: BLE001
            print("GraphQL failed, falling back to scrape:", e, file=sys.stderr)
    if not days:
        days, _ = scrape()
    if not days:
        sys.exit("no contribution data found")
    out = {"username": USERNAME,
           "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "days": days}
    (DATA / "contributions.json").write_text(json.dumps(out, indent=1))
    if repos is not None:
        (DATA / "repos.json").write_text(json.dumps(repos, indent=1))
    print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions,"
          f" {len(repos or [])} repos")


if __name__ == "__main__":
    main()
