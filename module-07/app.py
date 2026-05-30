import sys
from flask import Flask, render_template

app = Flask(__name__)

KPIS = [
    {"label": "KPI 1", "value": "128", "subtitle": "Total Notes"},
    {"label": "KPI 2", "value": "42",  "subtitle": "Active Tasks"},
    {"label": "KPI 3", "value": "7d",  "subtitle": "Current Streak"},
]

RECENT_ITEMS = [
    {"name": "Meeting notes — Q2 planning",        "value": "2026-05-29"},
    {"name": "Bug report: login timeout",           "value": "2026-05-28"},
    {"name": "Design review feedback",              "value": "2026-05-27"},
    {"name": "Sprint retrospective summary",        "value": "2026-05-26"},
    {"name": "Onboarding checklist v3",             "value": "2026-05-25"},
]

NAV_LINKS = ["Overview", "Notes", "Tasks", "Reports", "Settings"]

@app.route("/")
def index():
    return render_template(
        "index.html",
        kpis=KPIS,
        recent_items=RECENT_ITEMS,
        nav_links=NAV_LINKS,
        active_link="Overview",
    )

if __name__ == "__main__":
    app.run(debug=True, port=8080)
