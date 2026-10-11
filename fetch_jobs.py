import json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

KEY = os.environ.get("RAPIDAPI_KEY", "")
QUERY = "data analyst in India"   # change this to search for something else
PAGES = 2                         # 10 jobs per page, 1 API request per page
KEEP_DAYS = 21                    # drop jobs older than this
MAX_JOBS = 60                     # most jobs kept in jobs.json
OUT = "jobs.json"


def fetch(page):
    params = urllib.parse.urlencode({
        "query": QUERY, "page": page, "num_pages": 1,
        "date_posted": "week", "country": "in",
    })
    req = urllib.request.Request(
        "https://jsearch.p.rapidapi.com/search?" + params,
        headers={"X-RapidAPI-Key": KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r).get("data", [])


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
    new = []
    for p in range(1, PAGES + 1):
        try:
            new += [c for c in map(convert, fetch(p)) if c]
        except Exception as e:
            print("page", p, "failed:", e)
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
