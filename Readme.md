# qadam.

Take it one step at a time. A Flask app that helps parents and grandparents gain digital confidence through short lessons, safe practice rooms, a scam quiz, the Scam Dojo and a confidence score.

## Run

```bash
python -m venv venv
venv\Scripts\activate        
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Settings (optional)

Copy `.env.example` to `.env` and fill it in:

- `GEMINI_API_KEY` : Scam Dojo ko har baar naya message milta hai. Bina key ke 11 pehle se likhe messages chalte hain.
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` : pehla admin account (default `admin@example.com` / `admin123`, sirf testing ke liye). `ADMIN_PASSWORD` set ho to har start par admin ka password wohi ho jata hai.
- `SECRET_KEY` : cookies ke liye lambi random string.

## Scam Dojo (`/dojo`)

1. User ko SMS/WhatsApp message dikhta hai. Jawab server par chhupa rehta hai.
2. "Real or Scam?" dabane par verdict, red/green highlights aur wajah, "Seedhi baat" aur "Kya karein" milte hain.
3. "Suno" jawab bol kar sunata hai. "Agla message" naya message laata hai.
4. Taqreeban 65% messages scam, baqi asli.
5. Source: Gemini (9 scam topics, 6 asli topics, jawab validate hota hai, galat ho to reject), warna `data/scam_fallback.py` (6 scam, 5 asli) aur admin ke add kiye messages.
6. Har check par `/api/progress` ko `kind: dojo` bheja jata hai.

## Accounts

Register (naam, email, password) aur Login email + password se (`/register`, `/login`). Email ka format check hota hai, password kam az kam 8 harf, harf aur number dono. Passwords hashed save hote hain. Home ke ilawa baqi sab pages login ke baad. Progress user ke account se juda hai, har device par milta hai. Register karte waqt login se pehle ka progress account mein aa jata hai. 5 ghalat koshishon ke baad 5 minute ka rukawat.

Roles: `user` aur `admin`. Admin `/admin` kholta hai (login ke baad nav mein "Admin" link).

## Dashboard (`/path`)

User ka progress: lessons, practice rooms, safety quiz, Dojo checks, confidence score, badges aur agla qadam.

## Admin (`/admin`)

Sirf admin role. Overview stats, saare users aur unka progress, Safety quiz ke sawal add/delete, Scam Dojo messages add/delete. Sab SQLite mein save hota hai.

## What is real and what is simulated

- Real: lessons, progress saved in SQLite per browser (anonymous cookie), confidence score, read aloud (browser text-to-speech).
- Simulated: bank, form and video call practice rooms (nothing is connected to anything real).
- The Helper uses a built-in keyword guide, not a live AI.

## Structure

`app.py` routes and API, `database.py` SQLite, `data/` content, `templates/` pages, `static/` CSS and JS.


## Practice rooms (`/practice`)

Three simulated rooms with a coach panel: **Bank**, **Form** and **Video call**. Each step expects one action. A wrong tap gets a kind message, "I'm stuck" shows a hint, and "Suno" reads the instruction aloud.

- **Bank Sandbox:** fake banking app (demo balance Rs 25,000). The **Undo** button steps back, and the app reminds the user that real banks usually cannot reverse a sent payment, so check the name first.
- **Video Call Rehearsal:** uses the browser's real `getUserMedia` camera/mic permission, shows a live self-preview, and really mutes/unmutes the mic. If there is no camera, the page is not secure, or the device has none, it falls back to pretending. A blocked permission shows how to allow it.
- Finishing a room saves `practice` progress (`bank`, `form`, `video`), which feeds the confidence score.
- A room can be opened directly with a link such as `/practice#bank`.

Limitation: the bank and form rooms are fake interfaces. No real banking or real data is used.