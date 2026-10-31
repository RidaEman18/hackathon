"""The only file that talks to SQLite."""
import json
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
        # Accounts. role: "user" ya "admin"
        c.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT UNIQUE COLLATE NOCASE NOT NULL, "
            "pw_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', "
            "created TEXT DEFAULT CURRENT_TIMESTAMP, email TEXT, name TEXT)"
        )
        # Purani database.db ke liye: email aur name columns jodo
        cols = [r["name"] for r in c.execute("PRAGMA table_info(users)")]
        for col in ("email", "name"):
            if col not in cols:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        c.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_email ON users(email COLLATE NOCASE)")
        # Admin ke add kiye hue safety quiz sawal
        c.execute(
            "CREATE TABLE IF NOT EXISTS quiz_questions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, msg TEXT, "
            "answer INTEGER, why TEXT)"
        )
        # Admin ke add kiye hue Scam Dojo messages (poora item JSON mein)
        c.execute(
            "CREATE TABLE IF NOT EXISTS dojo_messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT)"
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
    dojo = len([r for r in rows if r["kind"] == "dojo"])
    # Confidence score: tutorials 40 + practice rooms 30 + quiz 30
    score = round(
        len(tut) / total_tutorials * 40 + min(len(prac), 3) / 3 * 30 + quiz / 100 * 30
    )
    return {"tutorials": tut, "practice": prac, "quiz": quiz, "dojo": dojo,
            "score": score, "level": level_for(score)}


# ---- Safety quiz sawal (admin) ---------------------------------------------
def custom_quiz():
    """Admin ke sawal, quiz.py wali shakal mein (from, msg, answer, why)."""
    with conn() as c:
        rows = c.execute("SELECT * FROM quiz_questions ORDER BY id").fetchall()
    return [{"id": r["id"], "from": r["sender"], "msg": r["msg"],
             "answer": r["answer"], "why": r["why"]} for r in rows]


def add_quiz(sender, msg, answer, why):
    with conn() as c:
        c.execute(
            "INSERT INTO quiz_questions (sender, msg, answer, why) VALUES (?,?,?,?)",
            (sender, msg, answer, why),
        )


def delete_quiz(qid):
    with conn() as c:
        c.execute("DELETE FROM quiz_questions WHERE id = ?", (qid,))


# ---- Scam Dojo messages (admin) --------------------------------------------
def custom_dojo():
    with conn() as c:
        rows = c.execute("SELECT id, data FROM dojo_messages ORDER BY id").fetchall()
    out = []
    for r in rows:
        item = json.loads(r["data"])
        item["id"] = f"c-{r['id']}"
        item["db_id"] = r["id"]
        out.append(item)
    return out


def add_dojo(item):
    with conn() as c:
        c.execute("INSERT INTO dojo_messages (data) VALUES (?)", (json.dumps(item),))


def delete_dojo(did):
    with conn() as c:
        c.execute("DELETE FROM dojo_messages WHERE id = ?", (did,))


# ---- Admin stats -------------------------------------------------------------
def stats(total_tutorials):
    with conn() as c:
        users = c.execute("SELECT COUNT(DISTINCT uid) n FROM progress").fetchone()["n"]
        lessons = c.execute(
            "SELECT COUNT(*) n FROM progress WHERE kind='tutorial'").fetchone()["n"]
        practice = c.execute(
            "SELECT COUNT(*) n FROM progress WHERE kind='practice'").fetchone()["n"]
        dojo = c.execute(
            "SELECT COUNT(*) n FROM progress WHERE kind='dojo'").fetchone()["n"]
        avg = c.execute(
            "SELECT AVG(best) a FROM (SELECT MAX(value) best FROM progress "
            "WHERE kind='quiz' GROUP BY uid)").fetchone()["a"]
    return {"users": users, "lessons": lessons, "practice": practice,
            "dojo": dojo, "quiz_avg": round(avg) if avg is not None else None}


# ---- Accounts ----------------------------------------------------------------
# Login email se hota hai. 'username' column purani wajah se rehta hai aur email ke
# barabar save hota hai; dikhane ke liye 'name' use hota hai.
def create_user(email, name, pw_hash, role="user"):
    """User banao. Returns id, ya None agar email pehle se hai."""
    try:
        with conn() as c:
            cur = c.execute(
                "INSERT INTO users (username, email, name, pw_hash, role) VALUES (?,?,?,?,?)",
                (email, email, name, pw_hash, role),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user(user_id):
    with conn() as c:
        return c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_email(email):
    with conn() as c:
        return c.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()


def set_admin(email, pw_hash, force_password):
    """Pehla admin banao. force_password=True ho to hash env se update karo."""
    u = get_user_by_email(email)
    with conn() as c:
        # Purane (bina email wale) admin accounts ab login nahi kar sakte; role hata do.
        c.execute("UPDATE users SET role = 'user' WHERE email IS NULL AND role = 'admin'")
        if u is None:
            c.execute("INSERT INTO users (username, email, name, pw_hash, role) "
                      "VALUES (?,?,?,?, 'admin')", (email, email, "Admin", pw_hash))
        elif force_password:
            c.execute("UPDATE users SET pw_hash = ?, role = 'admin' WHERE id = ?",
                      (pw_hash, u["id"]))


def move_progress(old_uid, new_uid):
    """Register se pehle ka anonymous progress naye account mein le jao."""
    with conn() as c:
        c.execute("UPDATE OR IGNORE progress SET uid = ? WHERE uid = ?", (new_uid, old_uid))


def list_users(total_tutorials):
    with conn() as c:
        users = c.execute("SELECT id, email, name, role, created FROM users WHERE email IS NOT NULL ORDER BY id").fetchall()
    out = []
    for u in users:
        s = summary(f"u{u['id']}", total_tutorials)
        out.append({"name": u["name"], "email": u["email"], "role": u["role"], "created": u["created"],
                    "lessons": len(s["tutorials"]), "practice": len(s["practice"]),
                    "quiz": s["quiz"], "dojo": s["dojo"], "score": s["score"]})
    return out
