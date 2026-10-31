"""Form Whisperer: recognises a form field, explains it in English + Roman Urdu,
guides the learner through a whole form, and validates practice answers.
Registered in app.py as a Blueprint. Login is enforced by app.py's before_request."""
import difflib
import re
from datetime import date

from flask import Blueprint, jsonify, render_template, request

from data.form_fields import (ERRORS, FALLBACK, FIELD_BY_ID, FIELDS, GENERIC,
                              PRESETS)

bp = Blueprint("form_whisperer", __name__)

GENERIC_KEYS = {"name", "naam", "address", "pata"}


def view(f):
    """Only the safe, display-only parts of a field go to the browser."""
    return {k: f[k] for k in ("id", "name", "english", "tip_en", "urdu", "tip", "example")}


def norm(text):
    return " ".join(re.sub(r"[^a-z0-9/@.+ -]", " ", text.lower()).split())


def has_phrase(text, phrase):
    return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None


def recognise(raw):
    """Return (best_field, matched_by, ranked) for a label or a typed value."""
    text = norm(raw)
    tokens = re.findall(r"[a-z]+", text)
    scores = {}
    for f in FIELDS:
        score, by = 0, "label"
        shape = f.get("shape")
        if shape and re.match(shape, raw.strip()):
            score, by = score + 10, "value"          
        for key in f["keys"]:
            k = norm(key)
            if has_phrase(text, k):
                score += 1 if k in GENERIC_KEYS else 3 * len(k.split())
            elif " " not in k and len(k) >= 5 and difflib.get_close_matches(k, tokens, n=1, cutoff=0.84):
                score += 2                            # tolerate typos: "domicil", "mobil"
        if score:
            scores[f["id"]] = (score, by)
    ranked = sorted(scores, key=lambda i: -scores[i][0])
    if not ranked:
        return None, None, []
    return FIELD_BY_ID[ranked[0]], scores[ranked[0]][1], ranked[1:4]


# ------------------------------------------------------------------- validation
def _name(v, min_words=1):
    v = v.strip()
    if re.search(r"\d", v): return "digits"
    if len(v) < 3: return "short"
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'\-]+", v): return "chars"
    if len(v.split()) < min_words: return "oneword"
    return None


def _text(v, min_len=3):
    return "short" if len(v.strip()) < min_len else ("digits" if re.search(r"\d", v) else None)


def v_cnic(v):
    if re.search(r"[A-Za-z]", v): return "letters", None, 0
    d = re.sub(r"\D", "", v)
    if len(d) != 13: return "length", None, len(d)
    return None, f"{d[:5]}-{d[5:12]}-{d[12]}", 0


def v_dob(v):
    m = re.fullmatch(r"\s*(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\s*", v)
    if not m:
        return ("order" if re.fullmatch(r"\s*\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\s*", v) else "format"), None, 0
    d, mo, y = map(int, m.groups())
    try:
        dt = date(y, mo, d)
    except ValueError:
        return "invalid", None, 0
    if dt > date.today(): return "future", None, 0
    if date.today().year - y > 110: return "old", None, 0
    return None, f"{d:02d}-{mo:02d}-{y}", 0


def v_mobile(v):
    s = re.sub(r"[\s-]", "", v)
    if re.search(r"[A-Za-z]", s): return "letters", None, 0
    m = re.fullmatch(r"(?:\+92|0092|92|0)?(3\d{9})", s)
    if not m: return "format", None, 0
    n = m.group(1)
    return None, f"0{n[:3]}-{n[3:]}", 0


def v_email(v):
    v = v.strip()
    if re.search(r"\s", v): return "space", None, 0
    if "@" not in v: return "noat", None, 0
    if "." not in v.split("@")[-1]: return "nodot", None, 0
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]{2,}", v): return "format", None, 0
    return None, v.lower(), 0


def v_nextkin(v):
    if not re.search(r"0?3\d{2}[-\s]?\d{7}", v): return "nophone", None, 0
    if not re.search(r"[A-Za-z]{2,}", v): return "noname", None, 0
    return None, None, 0


def v_income(v):
    s = re.sub(r"(?i)rs\.?|rupees|[,\s]", "", v)
    return (None, s, 0) if re.fullmatch(r"\d{3,9}", s) else ("digits", None, 0)


VALIDATORS = {
    "fullname": lambda v: (_name(v, 2), None, 0),
    "father": lambda v: (_name(v), None, 0),
    "signature": lambda v: (_name(v), None, 0),
    "cnic": v_cnic, "dob": v_dob, "mobile": v_mobile, "email": v_email,
    "nextkin": v_nextkin, "income": v_income,
    "address": lambda v: ("short" if len(v.strip()) < 10 or len(v.split()) < 3 else None, None, 0),
    "mailing": lambda v: (None, None, 0) if re.fullmatch(r"(?i)\s*same as (permanent|home)\s*", v)
    else ("short" if len(v.strip()) < 10 or len(v.split()) < 3 else None, None, 0),
    "domicile": lambda v: (_text(v), None, 0),
    "occupation": lambda v: (_text(v), None, 0),
    "nationality": lambda v: (_text(v), None, 0),
    "declaration": lambda v: (None, None, 0) if re.search(r"(?i)\b(i )?(agree|accept|confirm|yes|haan)\b", v) else ("agree", None, 0),
}


def message(field_id, code, n=0):
    en, ur = ERRORS.get(field_id, {}).get(code) or GENERIC.get(code, GENERIC["short"])
    return en.format(n=n), ur.format(n=n)


# ---------------------------------------------------------------------- routes
@bp.route("/form-whisperer")
def page():
    return render_template("form_whisperer.html")


@bp.route("/api/form-whisperer", methods=["POST"])
def explain():
    """Explain one field, from its label (or from a value the learner typed)."""
    text = str((request.get_json(silent=True) or {}).get("text", "")).strip()[:300]
    if not text:
        return jsonify(error="Please type a field name first."), 400
    best, by, others = recognise(text)
    if best is None:
        return jsonify(found=False, id="", example="", **FALLBACK)
    return jsonify(found=True, matched=by, alternatives=[{"id": i, "name": FIELD_BY_ID[i]["name"]} for i in others],
                   **view(best))


@bp.route("/api/form-whisperer/scan", methods=["POST"])
def scan():
    """Paste a form's field labels (one per line). Returns the fields we recognise, in order."""
    raw = str((request.get_json(silent=True) or {}).get("text", ""))[:3000]
    lines = [s.strip() for s in re.split(r"[\n;,]+", raw) if s.strip()][:30]
    if not lines:
        return jsonify(error="Please paste at least one field name."), 400
    fields, unknown, seen = [], [], set()
    for line in lines:
        f, _, _ = recognise(line[:80])
        if f is None:
            unknown.append(line[:80])
        elif f["id"] not in seen:
            seen.add(f["id"])
            fields.append(view(f))
    return jsonify(fields=fields, unknown=unknown)


@bp.route("/api/form-whisperer/presets")
def presets():
    return jsonify(presets=[{"id": p["id"], "title": p["title"],
                             "fields": [view(FIELD_BY_ID[i]) for i in p["fields"]]} for p in PRESETS])


@bp.route("/api/form-whisperer/check", methods=["POST"])
def check():
    """Validate a practice answer and explain mistakes kindly. Nothing is stored."""
    d = request.get_json(silent=True) or {}
    fid, value = str(d.get("field", "")), str(d.get("value", ""))[:300]
    if fid not in VALIDATORS:
        return jsonify(error="Unknown field."), 400
    if not value.strip():
        code, norm_value, n = "empty", None, 0
    else:
        code, norm_value, n = VALIDATORS[fid](value)
    f = FIELD_BY_ID[fid]
    if code is None:
        tidy = f" Usual way to write it: {norm_value}" if norm_value and norm_value != value.strip() else ""
        return jsonify(ok=True, en=f"Correct! That is how {f['name']} is usually written.{tidy}",
                       ur="Bilkul theek! Aap ne yeh field sahi bhara. Shabash!", normalized=norm_value)
    en, ur = message(fid, code, n)
    return jsonify(ok=False, code=code, example=f["example"],
                   en=f"No worries, mistakes help us learn. {en} Try like this: {f['example']}",
                   ur=f"Koi baat nahi, ghalti se hi seekhte hain. {ur} Is tarah likhein: {f['example']}")
