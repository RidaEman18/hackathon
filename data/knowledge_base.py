"""Built-in guide for the Helper. Not a live AI: it matches keywords."""

SUGGESTED = ["Is this message a scam?", "How do I join a video call?",
             "How do I send money safely?", "What is an OTP?"]

ENTRIES = [
    {"keys": ["scam", "fraud", "suspicious", "link", "prize", "won", "fake"],
     "short": "If a message scares you or promises money, treat it as a scam.",
     "simple": "Scammers want you to hurry or feel excited. Real banks do not do that.",
     "next": "Do not tap the link. Do not reply. Try the Safety quiz."},
    {"keys": ["otp", "pin", "code", "cvv"],
     "short": "An OTP or PIN is a private key to your money.",
     "simple": "It is a secret number. If someone asks for it, they want your money.",
     "next": "Never share it, not even with someone saying they are from the bank."},
    {"keys": ["video", "call", "zoom", "meet", "camera", "mic", "microphone", "mute"],
     "short": "Open the link, tap Allow for camera and mic, then tap Join.",
     "simple": "Tap the link. Tap Allow. Tap Join. A mic with a line means muted.",
     "next": "Practice this in the Video Call room first."},
    {"keys": ["bank", "money", "transfer", "send", "payment", "balance"],
     "short": "Log in with your own PIN, read the name and number twice, then confirm.",
     "simple": "Check who you are sending to. Then check again. Then confirm.",
     "next": "Try the Bank practice room. Nothing there is real."},
    {"keys": ["password", "login", "forgot"],
     "short": "Use a long phrase and a different password for email and bank.",
     "simple": "A long sentence is stronger than one word. Keep a paper copy at home.",
     "next": "Open the lesson 'Make a strong password'."},
    {"keys": ["whatsapp", "message", "chat", "text"],
     "short": "Open WhatsApp, tap the green button, pick a person, type, tap the arrow.",
     "simple": "Green button, name, type, green arrow. Two ticks = delivered.",
     "next": "Open the lesson 'Send a WhatsApp message'."},
    {"keys": ["form", "cnic", "id", "submit", "application", "government"],
     "short": "Read the whole form first and match your name to your ID card.",
     "simple": "Look at everything first. Copy your name exactly from your ID.",
     "next": "Try the Form practice room."},
]

FALLBACK = {
    "short": "I do not have an answer for that yet.",
    "simple": "Sorry, my guide does not know this one.",
    "next": "Try one of the suggested questions, or ask a family member.",
}


def answer(q):
    words = set(q.lower().replace("?", " ").replace(",", " ").split())
    best, best_score = None, 0
    for e in ENTRIES:
        sc = len(words & set(e["keys"]))
        if sc > best_score:
            best, best_score = e, sc
    e = best or FALLBACK
    return {"short": e["short"], "simple": e["simple"], "next": e["next"]}
