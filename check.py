#!/usr/bin/env python3
"""Daily check for orlexglobal.com QR label pages and domain expiry.

Fails (exit 1) and writes report.md if:
  - any QR page (01/<GTIN>/10/<LOT>/) or /etiket/ does not return HTTP 200
  - any page's content differs from the baseline sha256
  - orlexglobal.com expires in fewer than WARN_DAYS days
No Claude / AI involved; runs on GitHub Actions for free.
"""
import hashlib, json, sys, urllib.request, datetime
from concurrent.futures import ThreadPoolExecutor

SITE = "https://orlexglobal.com/"
RDAP = "https://rdap.verisign.com/com/v1/domain/orlexglobal.com"
WARN_DAYS = 90
UA = {"User-Agent": "orlex-monitor/1.0"}

def get(url, tries=3):
    last = None
    for _ in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            last = (e.code, b"")
        except Exception as e:  # network hiccup: retry
            last = (0, str(e).encode())
    return last

def page_url(path):
    if path == "CNAME":
        return None  # not served as a page; repo check covers it
    return SITE + path[: -len("index.html")] if path.endswith("index.html") else SITE + path

def check(line):
    want, path = line.split(None, 1)
    url = page_url(path)
    if not url:
        return None
    code, body = get(url)
    if code != 200:
        return f"- `{url}` → HTTP {code or 'no response'}"
    if hashlib.sha256(body).hexdigest() != want:
        return f"- `{url}` → içerik değişmiş (beklenen dosyayla aynı değil)"
    return None

def main():
    lines = [l for l in open("baseline.sha256", encoding="utf-8").read().splitlines() if l.strip()]
    with ThreadPoolExecutor(8) as ex:
        problems = [p for p in ex.map(check, lines) if p]

    code, body = get(SITE)
    if code != 200:
        problems.insert(0, f"- Ana sayfa `{SITE}` → HTTP {code or 'no response'}")

    days_left = None
    try:
        code, body = get(RDAP)
        ev = json.loads(body)["events"]
        exp = next(e["eventDate"] for e in ev if e["eventAction"] == "expiration")
        exp_dt = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
        days_left = (exp_dt - datetime.datetime.now(datetime.timezone.utc)).days
        if days_left < WARN_DAYS:
            problems.insert(0, f"- **orlexglobal.com alan adının süresi {days_left} gün sonra bitiyor ({exp_dt:%d.%m.%Y}).** İsimtescil'de hemen uzatın.")
    except Exception as e:
        problems.append(f"- Alan adı bitiş tarihi okunamadı ({e})")

    checked = sum(1 for l in lines if page_url(l.split(None, 1)[1]))
    today = datetime.date.today().isoformat()
    head = f"Kontrol: {today} · {checked} sayfa · alan adı bitişine {days_left} gün"
    if problems:
        report = f"## ORLEX QR kontrolü BAŞARISIZ\n\n{head}\n\n" + "\n".join(problems[:200])
        if len(problems) > 200:
            report += f"\n\n…ve {len(problems)-200} sorun daha."
    else:
        report = f"## ORLEX QR kontrolü: sorun yok\n\n{head}\n"
    open("report.md", "w", encoding="utf-8").write(report)
    print(report)
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
