import json, os, re, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

KEY = os.environ.get("RAPIDAPI_KEY", "").strip()
QUERY = "data analyst in India"   # change this to search for something else
PAGES = 2                         # about 10 jobs per page, 1 API request per page
KEEP_DAYS = 21                    # drop jobs older than this
MAX_JOBS = 60                     # most jobs kept in jobs.json
OUT = "jobs.json"

# JSearch now uses the /search-v2 endpoint. The same endpoint is offered on RapidAPI
# and directly on OpenWeb Ninja, so we try both with the key you saved.
SOURCES = [
    ("https://jsearch.p.rapidapi.com/search-v2",
     {"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}),
    ("https://api.openwebninja.com/jsearch/search-v2",
     {"x-api-key": KEY}),
]
working = None


def fetch(cursor):
    global working
    params = {"query": QUERY, "country": "in", "language": "en", "date_posted": "week"}
    if cursor:
        params["cursor"] = cursor
    qs = urllib.parse.urlencode(params)
    order = [working] if working is not None else range(len(SOURCES))
    last = None
    for i in order:
        base, headers = SOURCES[i]
        try:
            req = urllib.request.Request(base + "?" + qs, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.load(r)
            working = i
            return body
        except urllib.error.HTTPError as e:
            print("source", i, "->", "HTTP", e.code, e.reason)
            last = e
        except Exception as e:
            print("source", i, "->", e)
            last = e
    raise last


def parse(body):
    d = body.get("data", body)
    if isinstance(d, list):
        return d, None
    return d.get("jobs") or [], d.get("cursor")


def level(title):
    t = title.lower()
    if re.search(r"\b(senior|sr|lead|manager|principal|head|director)\b", t):
        return "Experienced"
    if re.search(r"\b(junior|jr|fresher|freshers|intern|trainee|entry|graduate)\b", t):
        return "Fresher"
    return ""


def convert(j):
    title = (j.get("job_title") or "").strip()
    url = j.get("job_apply_link") or ""
    if not title or not url.startswith("http"):
        return None
    loc = ", ".join(x for x in [j.get("job_city"), j.get("job_state") or j.get("job_country")] if x)
    if j.get("job_is_remote"):
        loc = (loc + " (Remote)").strip()
    date = (j.get("job_posted_at_datetime_utc") or "")[:10] or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "id": j.get("job_id") or url,
        "title": title,
        "company": j.get("employer_name") or "",
        "loc": loc,
        "level": level(title),
        "source": j.get("job_publisher") or "",
        "url": url,
        "date": date,
    }


def main():
    if not KEY:
        sys.exit("RAPIDAPI_KEY is not set")
    try:
        old = json.load(open(OUT, encoding="utf-8")).get("jobs", [])
    except Exception:
        old = []
    new, cursor = [], None
    for p in range(PAGES):
        try:
            body = fetch(cursor)
        except Exception as e:
            print("request", p + 1, "failed:", e)
            break
        jobs, cursor = parse(body)
        if not jobs:
            print("no jobs in response:", json.dumps(body)[:300])
        new += [c for c in map(convert, jobs) if c]
        if not cursor:
            break
    if not new:
        sys.exit("No jobs fetched, keeping the old jobs.json")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
    seen, merged = set(), []
    for j in new + old:
        k = (j["title"].lower(), j["company"].lower(), j["loc"].lower())  # same job on several boards
        if k in seen or j["date"] < cutoff:
            continue
        seen.add(k)
        merged.append(j)
    merged.sort(key=lambda j: j["date"], reverse=True)
    out = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "jobs": merged[:MAX_JOBS]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("fetched", len(new), "| saved", len(out["jobs"]))


main()
