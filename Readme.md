# qadam.

Take it one step at a time. A Flask app that helps parents and grandparents gain digital confidence through short lessons, safe practice rooms, a scam quiz and a confidence score.

## Run

```bash
python -m venv venv
venv\Scripts\activate        
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## What is real and what is simulated

- Real: lessons, progress saved in SQLite per browser (anonymous cookie), confidence score, read aloud (browser text-to-speech).
- Simulated: bank, form and video call practice rooms (nothing is connected to anything real).
- The Helper uses a built-in keyword guide, not a live AI.

## Structure

`app.py` routes and API, `database.py` SQLite, `data/` content, `templates/` pages, `static/` CSS and JS.
