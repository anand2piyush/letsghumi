# LetsGhumi Tourism Web App

FastAPI, HTML, CSS, and JavaScript web app for a tourism website with public trip pages and a hardcoded owner dashboard.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Owner Login

- URL: `http://127.0.0.1:8000/owner`
- Username: `admin`
- Password: `letsghumi2026`

## Content Notes

- Public cards and settings are stored in `data/site.json`.
- Uploaded tour images are saved in `static/uploads`.
- To add the guide photo, place one of these files in `static/`: `guide.jpeg`, `guide.jpg`, or `guide.png`.
- Use the owner page to add up to 50 home Instagram links and up to 10 Instagram links per travel card.
