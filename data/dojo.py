"""Scam Dojo ka dimagh: message chunna, Gemini se banwana, jawab check karna.

Jawab (is_scam, highlights...) sirf server par rehta hai. Browser ko sirf
message ka text milta hai aur ek token. Jawab "check" par milta hai.
"""
import json
import os
import random
import secrets
import threading
import urllib.error
import urllib.request
import uuid
from collections import OrderedDict

from data.scam_fallback import REAL, SCAM

SCAM_SHARE = 0.65  # taqreeban 65% messages scam, baqi asli

SCAM_TOPICS = [
    "JazzCash ya Easypaisa account block hone ka dara",
    "BISP / Ehsaas ka nakli inaam jis mein CNIC aur OTP maanga jaye",
    "bank ya wallet ka OTP / PIN maangna",
    "parcel ya courier ki nakli fee aur nakli link",
    "ghar baithay naukri jis mein pehle registration fee ho",
    "bijli ya gas ka bill, connection katne ki dhamki",
    "ghar wale ke naam par naye number se paisay maangna",
    "lottery ya inaami scheme jis mein link kholna ho",
    "galti se paisay bhej diye, wapas karo ka bahana",
]
REAL_TOPICS = [
    "bank ka transaction alert jis mein koi link ya PIN na ho",
    "ghar wale (Ammi, Abbu, behan) ka aam sa message",
    "clinic ya school ka appointment reminder",
    "telecom company ka package reminder jo official app ki taraf bheje",
    "online order ki delivery ki khabar jis mein PIN/OTP na maanga jaye",
    "dost ka milne ka plan",
]

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# ---- token store: jawab server par ---------------------------------------
_PENDING = OrderedDict()
_LOCK = threading.Lock()
_MAX_PENDING = 500


def _remember(item):
    token = secrets.token_urlsafe(12)
    with _LOCK:
        _PENDING[token] = item
        while len(_PENDING) > _MAX_PENDING:
            _PENDING.popitem(last=False)
    return token


def lookup(token):
    with _LOCK:
        return _PENDING.get(token)


# ---- validation ------------------------------------------------------------
def validate(item):
    """True agar item theek hai. Gemini ka jawab yahan se guzarta hai."""
    try:
        text = item["text"]
        if not isinstance(text, str) or not (15 <= len(text) <= 500):
            return False
        if not isinstance(item["is_scam"], bool):
            return False
        for k in ("headline", "seedhi_baat", "kya_karein", "channel", "sender"):
            if not isinstance(item[k], str) or not item[k].strip():
                return False
        if item["channel"] not in ("SMS", "WhatsApp"):
            return False
        hl = item["highlights"]
        if not isinstance(hl, list) or not (1 <= len(hl) <= 6):
            return False
        reds = greens = 0
        for h in hl:
            if h.get("kind") not in ("red", "green"):
                return False
            ph, why = h.get("phrase"), h.get("why")
            if not isinstance(ph, str) or not ph or ph not in text:
                return False  # phrase message mein hona chahiye
            if not isinstance(why, str) or not why.strip():
                return False
            reds += h["kind"] == "red"
            greens += h["kind"] == "green"
        if item["is_scam"]:
            return reds >= 1            # scam mein kam az kam ek red flag
        return greens >= 1 and reds == 0  # asli mein sirf achi nishaniyan
    except (KeyError, TypeError, AttributeError):
        return False


def clean(item):
    """Sirf wohi fields rakho jo hamein chahiye, aur custom/gemini item ko id do."""
    return {
        "id": item.get("id") or "g-" + uuid.uuid4().hex[:8],
        "channel": item["channel"],
        "sender": item["sender"].strip()[:40],
        "text": item["text"].strip(),
        "is_scam": item["is_scam"],
        "headline": item["headline"].strip(),
        "highlights": [
            {"phrase": h["phrase"], "kind": h["kind"], "why": h["why"].strip()}
            for h in item["highlights"]
        ],
        "seedhi_baat": item["seedhi_baat"].strip(),
        "kya_karein": item["kya_karein"].strip(),
    }


# ---- Gemini ----------------------------------------------------------------
def _prompt(want_scam):
    topic = random.choice(SCAM_TOPICS if want_scam else REAL_TOPICS)
    kind = "SCAM" if want_scam else "ASLI (scam nahi)"
    rule = (
        "Kam az kam ek highlight kind 'red' ho. 'green' optional hai."
        if want_scam
        else "Sirf 'green' highlights ho, koi 'red' nahi. Kam az kam ek 'green'."
    )
    return f"""Tum Pakistan ke buzurgon ko scam pehchanna sikhane wali app ke liye ek chhota SMS ya WhatsApp message banate ho.

Message ki qism: {kind}
Topic: {topic}

Rules:
- Message Roman Urdu mein ho (Urdu English ke lafz mix ho sakte hain), 1 se 3 jumlay, 250 harf se kam.
- Kisi asli bank ya company ka asli link ya number mat likho. Scam ke liye nakli jaisa link banao.
- "highlights" mein 2 se 4 items. Har "phrase" message ke text mein hu-ba-hu (same spelling) maujood ho.
- Har "why" saadi Roman Urdu mein ek jumla.
- {rule}
- "seedhi_baat": 1-2 saaday jumlay. "kya_karein": 1-2 jumlay, amal karne wali baat.
- "headline": 1 chhota jumla.

Sirf JSON do, is shakal mein:
{{"channel": "SMS" ya "WhatsApp", "sender": "...", "text": "...", "is_scam": {str(want_scam).lower()},
  "headline": "...", "highlights": [{{"phrase": "...", "kind": "red" ya "green", "why": "..."}}],
  "seedhi_baat": "...", "kya_karein": "..."}}"""


def _call_gemini(want_scam, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = json.dumps({
        "contents": [{"parts": [{"text": _prompt(want_scam)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 1.0},
    }).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.load(r)
    raw = data["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw)


def from_gemini(want_scam):
    """Gemini se naya message. Kuch bhi galat ho to None (fallback chalega)."""
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    for _ in range(2):  # galat jawab ho to ek baar dobara koshish
        try:
            item = _call_gemini(want_scam, key)
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError,
                ValueError, OSError):
            continue
        if isinstance(item, dict) and item.get("is_scam") is want_scam and validate(item):
            return clean(item)
    return None


# ---- chunna ---------------------------------------------------------------
def pick(custom=(), last_id=None):
    """Agla message. Returns (item, source). 65% scam, 35% asli."""
    want_scam = random.random() < SCAM_SHARE
    item = from_gemini(want_scam)
    if item:
        return item, "gemini"
    pool = [m for m in list(SCAM if want_scam else REAL) + list(custom)
            if m["is_scam"] is want_scam]
    fresh = [m for m in pool if m["id"] != last_id] or pool
    return random.choice(fresh), "fallback"


def public_view(item, source):
    """Browser ko sirf yeh dikhta hai. Jawab nahi."""
    token = _remember({**item, "source": source})
    return {"token": token, "channel": item["channel"],
            "sender": item["sender"], "text": item["text"]}


def reveal(token):
    item = lookup(token)
    if not item:
        return None
    return {
        "id": item["id"],
        "is_scam": item["is_scam"],
        "verdict": "Yeh SCAM hai" if item["is_scam"] else "Yeh asli lagta hai",
        "headline": item["headline"],
        "highlights": item["highlights"],
        "seedhi_baat": item["seedhi_baat"],
        "kya_karein": item["kya_karein"],
        "source": item.get("source", "fallback"),
    }
