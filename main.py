"""Employee Onboarding Workflow."""
import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path


def add_business_days(d: date, n: int) -> date:
    step = 1 if n >= 0 else -1
    while n:
        d += timedelta(days=step)
        if d.weekday() < 5:
            n -= step
    return d


def plan(hire: dict, tpl: dict) -> list:
    start = date.fromisoformat(hire["start_date"])
    tasks = tpl["common"] + tpl["department"].get(hire["department"], [])
    tasks += tpl["remote" if hire["remote"] else "onsite"]
    out = []
    for t in tasks:
        due = add_business_days(start, t["offset"]) if t["offset"] else start
        owner = hire["manager"] if t["owner"] == "manager" else t["owner"]
        out.append({"task": t["task"].format(name=hire["name"]), "owner": owner,
                    "due": due.isoformat(), "status": hire.get("done", {}).get(t["task"], "pending")})
    return sorted(out, key=lambda x: x["due"])


def overdue(tasks, today):
    return [t for t in tasks if t["status"] != "done" and date.fromisoformat(t["due"]) < today]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hires", default="sample_hires.json")
    ap.add_argument("--today", default="2026-10-09")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    tpl = json.loads(Path("templates.json").read_text())
    today = date.fromisoformat(a.today)
    Path("output").mkdir(exist_ok=True)
    for h in json.loads(Path(a.hires).read_text()):
        tasks = plan(h, tpl)
        with open(f"output/onboarding_{h['name'].split()[0].lower()}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["task", "owner", "due", "status"])
            w.writeheader(); w.writerows(tasks)
        print(f"== {h['name']} | {h['role']} ({h['department']}) starts {h['start_date']} ==")
        for t in tasks:
            mark = "✔" if t["status"] == "done" else "!" if t in overdue(tasks, today) else " "
            print(f"  [{mark}] {t['due']}  {t['owner']:<10} {t['task']}")
        late = overdue(tasks, today)
        if late:
            print(f"  OVERDUE ({len(late)}): " + "; ".join(f"{t['owner']}: {t['task']}" for t in late))
        print(f"  Welcome: Hi {h['name'].split()[0]}, welcome to the team! On {h['start_date']} "
              f"{'join the 9am video call link in your email' if h['remote'] else 'please arrive at 9am at reception'}. "
              f"{h['manager']} will be your manager.\n")


if __name__ == "__main__":
    main()
