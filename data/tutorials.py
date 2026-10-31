"""Lessons. Each step: text, simple-words text, plus a picture of the app screen.
screen = which mock screen to show (see static/js/screens.js)
spot   = which part of that screen to point at (one id, or a list)
tip    = short caption under the picture

To use a REAL screenshot instead of a mock screen, save it in static/images/lessons/
and add shot="whatsapp1.png", box=(left, top, width, height) in percent of the image."""


def s(text, simple, screen, spot, tip, shot=None, box=None):
    d = {"text": text, "simple": simple, "screen": screen, "spot": spot, "tip": tip}
    if shot:
        d["shot"], d["box"] = shot, list(box or (0, 0, 100, 100))
    return d


TUTORIALS = [
    {"slug": "video-call", "title": "Join a video call", "icon": "📹", "steps": [
        s("Open the call link your family sent you.", "Tap the link in your message.",
          "vc_link", "link", "Tap this link"),
        s("When asked, tap Allow for the camera and microphone.", "Tap Allow. Now they can see and hear you.",
          "vc_allow", "allow", "Tap Allow"),
        s("Check the microphone button. A line through it means you are muted.", "Mic with a line through it = they cannot hear you.",
          "vc_lobby", "mic", "A line through the mic means muted"),
        s("Tap Join and say hello.", "Tap Join. Say hello!",
          "vc_lobby", "join", "Tap Join")]},
    {"slug": "banking", "title": "Use a banking app safely", "icon": "🏦", "steps": [
        s("Download the bank's app only from the official app store.", "Get the app from the Play Store or App Store only.",
          "bk_store", "official", "Pick the one with the tick, not the copy"),
        s("Log in with your own PIN. Never share it with anyone, even the bank.", "Your PIN is secret. Nobody should ask for it.",
          "bk_login", "pin", "Only you type your PIN"),
        s("Before sending money, read the name and number twice.", "Check the name. Check the number. Then check again.",
          "bk_send", ["name", "num"], "Read the name and number twice"),
        s("Log out when you are done.", "Tap Log out when finished.",
          "bk_home", "logout", "Tap Log out")]},
    {"slug": "scams", "title": "Spot a scam message", "icon": "🛡️", "steps": [
        s("Scam messages create panic: 'Your account will close today!'", "Scams try to scare you and make you hurry.",
          "sc_msg", "hurry", "A scam makes you hurry"),
        s("Banks never ask for your PIN, password or OTP code.", "Never tell anyone your PIN or OTP.",
          "sc_msg", "pin", "Banks never ask for your PIN"),
        s("Do not tap links in unknown messages.", "Unknown link? Do not tap it.",
          "sc_msg", "link", "Do not tap this link"),
        s("When unsure, call the bank on the number printed on your card.", "Not sure? Call the number on your bank card.",
          "sc_card", "num", "Call the number printed on your card")]},
    {"slug": "whatsapp", "title": "Send a WhatsApp message", "icon": "💬", "steps": [
        s("Open WhatsApp and tap the green chat button.", "Open WhatsApp. Tap the green button.",
          "wa_chats", "fab", "Tap the green button"),
        s("Pick the person you want to message.", "Tap the name of the person.",
          "wa_contacts", "ammi", "Tap the person's name"),
        s("Tap the box at the bottom and type your message.", "Tap the bottom box. Type.",
          "wa_chat", "box", "Tap here and type"),
        s("Tap the green arrow to send. Two ticks mean it was delivered.", "Tap the green arrow. Two ticks = sent.",
          "wa_sent", ["send", "ticks"], "Green arrow sends. Two ticks mean delivered")]},
    {"slug": "whatsapp-call", "title": "Make a WhatsApp call", "icon": "📞", "steps": [
        s("Open WhatsApp and tap the chat of the person you want to call.", "Open WhatsApp. Tap the person's name.",
          "wa_chats", "ammi", "Tap the person's name"),
        s("Tap the phone icon at the top for a voice call. The camera icon is for a video call.", "Phone icon = voice call. Camera icon = video call.",
          "wac_chat", "call", "Phone icon is a voice call. Camera icon is a video call"),
        s("Wait while it rings. The person will pick up.", "Wait. It is ringing.",
          "wac_ring", "who", "Wait for them to answer"),
        s("If the voice is too quiet, tap the speaker. A line through the microphone means they cannot hear you.", "Speaker = louder. Mic with a line = they cannot hear you.",
          "wac_in", ["spk", "mic"], "Speaker makes it louder. Check the mic has no line"),
        s("When you are done, tap the red button to end the call.", "Tap the red button to finish.",
          "wac_in", "end", "Tap the red button to end the call")]},
    {"slug": "phone-call", "title": "Make a normal phone call", "icon": "☎️", "steps": [
        s("Open the Phone app. It is usually a green phone icon.", "Tap the green phone icon.",
          "ph_home", "phoneapp", "Tap the Phone app"),
        s("Tap Contacts, then tap the name of the person you want to call.", "Tap Contacts. Tap the name.",
          "ph_contacts", "ammi", "Tap the person's name"),
        s("Or tap Keypad and type the number. Check the number before you call.", "Or type the number. Check it.",
          "ph_keypad", "num", "Check every digit of the number"),
        s("Tap the green call button.", "Tap the green button.",
          "ph_keypad", "callbtn", "Tap the green call button"),
        s("When you are done, tap the red button to end the call.", "Tap the red button to finish.",
          "ph_incall", "end", "Tap the red button to end the call"),
        s("When someone calls you, tap the green button to answer. Red means decline.", "Green = answer. Red = no.",
          "ph_incoming", ["answer", "decline"], "Green answers. Red declines")]},
    {"slug": "forms", "title": "Fill an online form", "icon": "📝", "steps": [
        s("Read the whole form once before typing anything.", "Look at the whole form first.",
          "fm_form", "all", "Read everything first"),
        s("Write your name exactly as it appears on your ID card.", "Name must match your ID card.",
          "fm_form", "name", "Same spelling as your ID card"),
        s("Check every field once more before submitting.", "Read everything again.",
          "fm_form", ["name", "cnic", "mobile"], "Check each box again"),
        s("Tap Submit only once and wait for the confirmation.", "Tap Submit one time. Then wait.",
          "fm_form", "submit", "Tap Submit once, then wait")]},
    {"slug": "passwords", "title": "Make a strong password", "icon": "🔑", "steps": [
        s("Use a long phrase, not a single word.", "A long sentence is better than one word.",
          "pw_phrase", "field", "A long phrase is strong"),
        s("Do not use birthdays, phone numbers or names.", "No birthdays. No phone numbers.",
          "pw_bad", "field", "A birthday is easy to guess"),
        s("Use a different password for your email and your bank.", "Do not use one password everywhere.",
          "pw_two", ["email", "bank"], "A different password for each"),
        s("Write it in a notebook kept at home, not in your phone.", "Keep a paper notebook at home.",
          "pw_note", "book", "Keep it on paper, at home")]},
]
