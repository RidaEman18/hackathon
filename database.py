"""The only file that talks to SQLite."""
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS progress ("
            "uid TEXT, kind TEXT, key TEXT, value INTEGER DEFAULT 1, "
            "PRIMARY KEY (uid, kind, key))"
        )


def save(uid, kind, key, value=1):
    """Save progress; for repeated saves keep the best value."""
    with conn() as c:
        c.execute(
            "INSERT INTO progress (uid, kind, key, value) VALUES (?,?,?,?) "
            "ON CONFLICT(uid, kind, key) DO UPDATE SET value = MAX(value, excluded.value)",
            (uid, kind, key, value),
        )


def level_for(score):
    if score >= 80:
        return "Digital Pro"
    if score >= 50:
        return "Confident"
    if score >= 25:
        return "Getting comfortable"
    return "Just starting"


def summary(uid, total_tutorials):
    with conn() as c:
        rows = c.execute(
            "SELECT kind, key, value FROM progress WHERE uid = ?", (uid,)
        ).fetchall()
    tut = sorted(r["key"] for r in rows if r["kind"] == "tutorial")
    prac = sorted(r["key"] for r in rows if r["kind"] == "practice")
    quiz = max([r["value"] for r in rows if r["kind"] == "quiz"] or [0])
    # Confidence score: tutorials 40 + practice rooms 30 + quiz 30
    score = round(
        len(tut) / total_tutorials * 40 + min(len(prac), 3) / 3 * 30 + quiz / 100 * 30
    )
    return {"tutorials": tut, "practice": prac, "quiz": quiz,
            "score": score, "level": level_for(score)}
