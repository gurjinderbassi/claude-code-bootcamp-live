# Module 07 — Dashboard Web App

**Track A: Flask + Jinja templates**

A single-page dashboard built with Flask and plain CSS, matching the provided wireframe at 1280×720.

## Run

```
python app.py
```

Then open http://localhost:8080 in your browser.

> **Note:** macOS reserves port 5000 for AirPlay Receiver — this app uses port 8080 instead.

## Stack

- Python 3.11+ / Flask 3.x
- Jinja2 templates (bundled with Flask)
- Plain CSS (no Tailwind, no component libraries)
- Static hardcoded sample data — no database, no auth

## Structure

```
module-07/
├── app.py               # Flask app + hardcoded data
├── templates/
│   └── index.html       # Jinja template
├── static/
│   └── style.css        # All styles
└── README.md
```
