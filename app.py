import os
import uuid

from flask import Flask, abort, jsonify, render_template, request, session

import database as db
from data.knowledge_base import answer
from data.quiz import QUIZ
from data.tutorials import TUTORIALS

app = Flask(__name__)
# Set SECRET_KEY in your environment for real use.
app.secret_key = os.environ.get("SECRET_KEY", "qadam-dev-key-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
)
db.init_db()


def current_uid():
    """Each browser gets a private anonymous id (no passwords)."""
    if "uid" not in session:
        session["uid"] = uuid.uuid4().hex
        session.permanent = True
    return session["uid"]


def progress():
    return db.summary(current_uid(), len(TUTORIALS))


@app.route("/")
def home():
    return render_template("index.html", tutorials=TUTORIALS)


@app.route("/path")
def dashboard():
    p = progress()
    nxt = next((t for t in TUTORIALS if t["slug"] not in p["tutorials"]), None)
    badges = []
    if p["tutorials"]:
        badges.append("First step taken")
    if p["practice"]:
        badges.append("Safe practiser")
    if len(p["tutorials"]) == len(TUTORIALS):
        badges.append("All lessons done")
    if p["quiz"] >= 80:
        badges.append("Scam spotter")
    return render_template("dashboard.html", tutorials=TUTORIALS, p=p, nxt=nxt, badges=badges)


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
    return render_template("safety.html", quiz=QUIZ)


@app.route("/api/progress", methods=["GET", "POST"])
def api_progress():
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        kind, key = d.get("kind"), str(d.get("key", ""))[:40]
        try:
            value = max(0, min(100, int(d.get("value", 1))))
        except (TypeError, ValueError):
            return jsonify(error="bad value"), 400
        if kind not in ("tutorial", "practice", "quiz") or not key:
            return jsonify(error="bad request"), 400
        db.save(current_uid(), kind, key, value)
    return jsonify(progress())


@app.route("/api/assistant", methods=["POST"])
def api_assistant():
    q = (request.get_json(silent=True) or {}).get("q", "")
    return jsonify(answer(str(q)[:300]))


@app.errorhandler(404)
def not_found(_):
    return render_template("index.html", tutorials=TUTORIALS), 404


if __name__ == "__main__":
    app.run(debug=True)
