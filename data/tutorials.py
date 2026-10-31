"""Lessons. Each step has normal text and a simple-words version."""


def s(text, simple):
    return {"text": text, "simple": simple}


TUTORIALS = [
    {"slug": "video-call", "title": "Join a video call", "icon": "📹", "steps": [
        s("Open the call link your family sent you.", "Tap the link in your message."),
        s("When asked, tap Allow for the camera and microphone.", "Tap Allow. Now they can see and hear you."),
        s("Check the microphone button. A line through it means you are muted.", "Mic with a line through it = they cannot hear you."),
        s("Tap Join and say hello.", "Tap Join. Say hello!")]},
    {"slug": "banking", "title": "Use a banking app safely", "icon": "🏦", "steps": [
        s("Download the bank's app only from the official app store.", "Get the app from the Play Store or App Store only."),
        s("Log in with your own PIN. Never share it with anyone, even the bank.", "Your PIN is secret. Nobody should ask for it."),
        s("Before sending money, read the name and number twice.", "Check the name. Check the number. Then check again."),
        s("Log out when you are done.", "Tap Log out when finished.")]},
    {"slug": "scams", "title": "Spot a scam message", "icon": "🛡️", "steps": [
        s("Scam messages create panic: 'Your account will close today!'", "Scams try to scare you and make you hurry."),
        s("Banks never ask for your PIN, password or OTP code.", "Never tell anyone your PIN or OTP."),
        s("Do not tap links in unknown messages.", "Unknown link? Do not tap it."),
        s("When unsure, call the bank on the number printed on your card.", "Not sure? Call the number on your bank card.")]},
    {"slug": "whatsapp", "title": "Send a WhatsApp message", "icon": "💬", "steps": [
        s("Open WhatsApp and tap the green chat button.", "Open WhatsApp. Tap the green button."),
        s("Pick the person you want to message.", "Tap the name of the person."),
        s("Tap the box at the bottom and type your message.", "Tap the bottom box. Type."),
        s("Tap the green arrow to send. Two ticks mean it was delivered.", "Tap the green arrow. Two ticks = sent.")]},
    {"slug": "forms", "title": "Fill an online form", "icon": "📝", "steps": [
        s("Read the whole form once before typing anything.", "Look at the whole form first."),
        s("Write your name exactly as it appears on your ID card.", "Name must match your ID card."),
        s("Check every field once more before submitting.", "Read everything again."),
        s("Tap Submit only once and wait for the confirmation.", "Tap Submit one time. Then wait.")]},
    {"slug": "passwords", "title": "Make a strong password", "icon": "🔑", "steps": [
        s("Use a long phrase, not a single word.", "A long sentence is better than one word."),
        s("Do not use birthdays, phone numbers or names.", "No birthdays. No phone numbers."),
        s("Use a different password for your email and your bank.", "Do not use one password everywhere."),
        s("Write it in a notebook kept at home, not in your phone.", "Keep a paper notebook at home.")]},
]
