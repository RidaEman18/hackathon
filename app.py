import hmac
import os
import re
import secrets
import time
import uuid
from functools import wraps

from flask import (Flask, abort, g, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env():
    """Chhota .env reader (GEMINI_API_KEY, ADMIN_PASSWORD, SECRET_KEY)."""
    path = os.path.join(HERE, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()

import database as db  # noqa: E402  (env pehle load hona chahiye)
from data import dojo  # noqa: E402
from data.knowledge_base import answer  # noqa: E402
from data.quiz import QUIZ  # noqa: E402
from data.tutorials import TUTORIALS  # noqa: E402

app = Flask(__name__)
# Set SECRET_KEY in your environment for real use.
app.secret_key = os.environ.get("SECRET_KEY", "qadam-dev-key-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)
db.init_db()

# Form Whisperer feature (own routes: /form-whisperer and /api/form-whisperer/*)
from form_whisperer import bp as form_whisperer_bp  # noqa: E402
app.register_blueprint(form_whisperer_bp)

# Pehla admin account. Default sirf testing ke liye hai.
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
USING_DEFAULT_ADMIN_PASSWORD = "ADMIN_PASSWORD" not in os.environ
DUMMY_HASH = generate_password_hash("dummy-password")
# ADMIN_PASSWORD env mein ho to har start par admin ka password wohi ho jata hai.
db.set_admin(ADMIN_EMAIL, generate_password_hash(ADMIN_PASSWORD),
             force_password=not USING_DEFAULT_ADMIN_PASSWORD)

# Email ka format: kuch@domain.tld (space ya do @ nahi)
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def valid_email(e):
    return len(e) <= 254 and bool(EMAIL_RE.match(e))


def password_problem(pw):
    if len(pw) < 8:
        return "Password kam az kam 8 harf ka ho."
    if not (re.search(r"[A-Za-z]", pw) and re.search(r"\d", pw)):
        return "Password mein harf aur number dono hon."
    if len(pw) > 128:
        return "Password bohat lamba hai."
    return None
PUBLIC_ENDPOINTS = {"static", "home", "login", "register"}


def current_uid():
    """Logged-in user ka progress 'u<id>' se juda hota hai."""
    if g.get("user"):
        return f"u{g.user['id']}"
    # Sirf logged-out hone par (home page); koi progress save nahi hota.
    if "uid" not in session:
        session["uid"] = uuid.uuid4().hex
        session.permanent = True
    return session["uid"]


@app.before_request
def load_user():
    g.user = db.get_user(session["user_id"]) if session.get("user_id") else None
    if request.endpoint is None or request.endpoint in PUBLIC_ENDPOINTS:
        return None
    if g.user is None:
        if request.path.startswith("/api/"):
            return jsonify(error="Pehle login karein."), 401
        return redirect(url_for("login", next=request.full_path.rstrip("?")))
    return None


@app.context_processor
def inject_user():
    return {"user": g.get("user")}


def progress():
    return db.summary(current_uid(), len(TUTORIALS))


# ---------------------------------------------------------------- user pages
@app.route("/")
def home():
    return render_template("index.html", tutorials=TUTORIALS)


def badge_list(p):
    """Badges earned so far (used by the dashboard and the certificate)."""
    badges = []
    if p["tutorials"]:
        badges.append("First step taken")
    if p["practice"]:
        badges.append("Safe practiser")
    if len(p["tutorials"]) == len(TUTORIALS):
        badges.append("All lessons done")
    if p["quiz"] >= 80:
        badges.append("Scam spotter")
    if p["dojo"] >= 10:
        badges.append("Dojo regular")
    return badges


@app.route("/path")
def dashboard():
    p = progress()
    nxt = next((t for t in TUTORIALS if t["slug"] not in p["tutorials"]), None)
    badges = badge_list(p)
    return render_template("dashboard.html", tutorials=TUTORIALS, p=p, nxt=nxt,
                           badges=badges, total=len(TUTORIALS))


@app.route("/certificate")
def certificate():
    """Printable Digital Confidence Certificate (login required by before_request)."""
    import hashlib
    from datetime import date
    p = progress()
    unlocked = bool(p["tutorials"] or p["practice"])
    who = (g.user["name"] or g.user["email"]) if g.user else "Learner"
    cert_no = "QDM-" + hashlib.sha1(current_uid().encode()).hexdigest()[:8].upper()
    return render_template("certificate.html", p=p, total=len(TUTORIALS), badges=badge_list(p),
                           unlocked=unlocked, who=who, cert_no=cert_no,
                           today=date.today().strftime("%d %B %Y"))


@app.route("/dashboard")
def dashboard_alias():
    return redirect(url_for("dashboard"))


@app.route("/learn")
def learn():
    return render_template("tutorials.html", tutorials=TUTORIALS, p=progress())


@app.route("/learn/<slug>")
def tutorial(slug):
    t = next((t for t in TUTORIALS if t["slug"] == slug), None)
    if t is None:
        abort(404)
    return render_template("tutorial.html", t=t)


@app.route("/practice")
def practice():
    return render_template("practice.html")


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/safety")
def safety():
    # Built-in sawal + admin ke add kiye hue sawal
    return render_template("safety.html", quiz=QUIZ + db.custom_quiz())


@app.route("/dojo")
def dojo_page():
    return render_template("dojo.html")


# ----------------------------------------------------------------------- API
@app.route("/api/progress", methods=["GET", "POST"])
def api_progress():
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        kind, key = d.get("kind"), str(d.get("key", ""))[:40]
        try:
            value = max(0, min(100, int(d.get("value", 1))))
        except (TypeError, ValueError):
            return jsonify(error="bad value"), 400
        if kind not in ("tutorial", "practice", "quiz", "dojo") or not key:
            return jsonify(error="bad request"), 400
        db.save(current_uid(), kind, key, value)
    return jsonify(progress())


@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    q = (request.get_json(silent=True) or {}).get("q", "")
    return jsonify(answer(str(q)[:300]))


@app.route("/api/dojo/next")
def api_dojo_next():
    """Naya message. Jawab (is_scam, highlights) is response mein NAHI hota."""
    item, source = dojo.pick(db.custom_dojo(), session.get("dojo_last"))
    session["dojo_last"] = item["id"]
    return jsonify(dojo.public_view(item, source))


@app.route("/api/dojo/check", methods=["POST"])
def api_dojo_check():
    token = str((request.get_json(silent=True) or {}).get("token", ""))
    result = dojo.reveal(token)
    if result is None:
        return jsonify(error="Yeh message purana ho gaya. 'Agla message' dabayein."), 404
    return jsonify(result)


# ------------------------------------------------------------------ accounts
FAILS = {}  # (ip, username) -> [waqt]; ghalat password ki koshishein
MAX_FAILS, WINDOW = 5, 300


def safe_next(url):
    """Sirf apni site ka raasta (open redirect se bachao)."""
    if url and url.startswith("/") and not url.startswith("//") and "\\" not in url:
        return url
    return None


def too_many_fails(key):
    now = time.time()
    FAILS[key] = [t for t in FAILS.get(key, []) if now - t < WINDOW]
    return len(FAILS[key]) >= MAX_FAILS


def log_in(user_id):
    session.clear()  # purani session ki cheezein nahi rakhte
    session["user_id"] = user_id
    session.permanent = True


@app.route("/login", methods=["GET", "POST"])
def login():
    nxt = safe_next(request.values.get("next"))
    if g.user:
        return redirect(nxt or url_for("dashboard"))
    error = None
    if request.method == "POST":
        check_csrf()
        email = request.form.get("email", "").strip().lower()
        key = (request.remote_addr, email)
        if not valid_email(email):
            error = "Sahi email likhein, jaise name@example.com."
        elif too_many_fails(key):
            error = "Bohat koshishein ho gayein. 5 minute baad dobara try karein."
        else:
            u = db.get_user_by_email(email)
            ok = check_password_hash(u["pw_hash"] if u else DUMMY_HASH,
                                     request.form.get("password", ""))
            if u and ok:
                FAILS.pop(key, None)
                log_in(u["id"])
                return redirect(nxt or (url_for("admin_home") if u["role"] == "admin"
                                        else url_for("dashboard")))
            FAILS.setdefault(key, []).append(time.time())
            error = "Email ya password ghalat hai."
    return render_template("login.html", error=error, next=nxt,
                           default_pw=USING_DEFAULT_ADMIN_PASSWORD)


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        check_csrf()
        name = " ".join(request.form.get("name", "").split())
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        if not (2 <= len(name) <= 50):
            error = "Apna naam likhein (2 se 50 harf)."
        elif not valid_email(email):
            error = "Sahi email likhein, jaise name@example.com."
        elif password_problem(pw):
            error = password_problem(pw)
        elif pw != request.form.get("confirm", ""):
            error = "Dono password ek jaise nahi hain."
        else:
            uid = db.create_user(email, name, generate_password_hash(pw))
            if uid is None:
                error = "Is email se account pehle se maujood hai. Login karein."
            else:
                old = session.get("uid")  # login se pehle ka progress saath le jao
                if old:
                    db.move_progress(old, f"u{uid}")
                log_in(uid)
                return redirect(url_for("dashboard"))
    return render_template("register.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


# --------------------------------------------------------------------- admin
def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def check_csrf():
    sent = request.form.get("csrf", "")
    if not hmac.compare_digest(sent, session.get("csrf", "")):
        abort(400)


def admin_required(view):
    @wraps(view)
    def wrapper(*a, **kw):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        if g.user["role"] != "admin":
            abort(403)
        return view(*a, **kw)
    return wrapper


@app.route("/admin/login")
def admin_login():
    return redirect(url_for("login", next="/admin"))


@app.route("/admin")
@admin_required
def admin_home():
    return render_template(
        "admin/home.html", s=db.stats(len(TUTORIALS)),
        users=db.list_users(len(TUTORIALS)),
        n_quiz=len(QUIZ) + len(db.custom_quiz()), n_dojo=len(db.custom_dojo()),
        gemini=bool(os.environ.get("GEMINI_API_KEY")),
        default_pw=USING_DEFAULT_ADMIN_PASSWORD)


@app.route("/admin/quiz", methods=["GET", "POST"])
@admin_required
def admin_quiz():
    error = None
    if request.method == "POST":
        check_csrf()
        if request.form.get("delete"):
            try:
                db.delete_quiz(int(request.form["delete"]))
            except ValueError:
                abort(400)
            return redirect(url_for("admin_quiz"))
        sender = request.form.get("sender", "").strip()[:80]
        msg = request.form.get("msg", "").strip()[:500]
        why = request.form.get("why", "").strip()[:300]
        try:
            ans = int(request.form.get("answer", ""))
        except ValueError:
            ans = -1
        if not (sender and msg and why) or ans not in (0, 1, 2):
            error = "Saari cheezein bharein aur sahi jawab chunein."
        else:
            db.add_quiz(sender, msg, ans, why)
            return redirect(url_for("admin_quiz"))
    return render_template("admin/quiz.html", builtin=QUIZ,
                           custom=db.custom_quiz(), error=error)


def parse_highlights(raw):
    """Har line: phrase | red ya green | wajah"""
    out = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            return None
        out.append({"phrase": parts[0], "kind": parts[1].lower(), "why": parts[2]})
    return out


@app.route("/admin/dojo", methods=["GET", "POST"])
@admin_required
def admin_dojo():
    error = None
    if request.method == "POST":
        check_csrf()
        if request.form.get("delete"):
            try:
                db.delete_dojo(int(request.form["delete"]))
            except ValueError:
                abort(400)
            return redirect(url_for("admin_dojo"))
        f = request.form
        highlights = parse_highlights(f.get("highlights", ""))
        item = {
            "channel": f.get("channel", ""),
            "sender": f.get("sender", "").strip(),
            "text": f.get("text", "").strip(),
            "is_scam": f.get("is_scam") == "1",
            "headline": f.get("headline", "").strip(),
            "highlights": highlights or [],
            "seedhi_baat": f.get("seedhi_baat", "").strip(),
            "kya_karein": f.get("kya_karein", "").strip(),
        }
        if highlights is None:
            error = "Highlights ki har line 'lafz | red ya green | wajah' shakal mein ho."
        elif not dojo.validate(item):
            error = ("Message check mein fail hua. Dekhein: har highlight ka lafz message mein "
                     "hu-ba-hu ho; scam mein kam az kam ek red; asli mein sirf green.")
        else:
            db.add_dojo(dojo.clean(item))
            return redirect(url_for("admin_dojo"))
    return render_template("admin/dojo.html", custom=db.custom_dojo(), error=error)


@app.errorhandler(404)
def not_found(_):
    return render_template("index.html", tutorials=TUTORIALS), 404


if __name__ == "__main__":
    app.run(debug=True)
