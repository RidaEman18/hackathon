"""Scam quiz. 'answer' is the index of the correct option."""
OPTIONS = ["Scam", "Real", "Not sure, I'll call the bank"]

QUIZ = [
    {"from": "SMS from 'Bank'", "msg": "Dear customer, your account will be blocked in 2 hours. Send your PIN to this number to keep it open.",
     "answer": 0, "why": "Banks never ask for your PIN. The hurry is a trick."},
    {"from": "WhatsApp, unknown number", "msg": "Congratulations! You won Rs 500,000. Tap this link to claim your prize.",
     "answer": 0, "why": "You cannot win a contest you never entered. Do not tap the link."},
    {"from": "Bank app notification", "msg": "Your monthly statement is ready. Open the official app to view it.",
     "answer": 1, "why": "It asks for nothing and tells you to use the official app. Looks normal."},
    {"from": "Email, 'Customer Care'", "msg": "We sent a code to your phone. Please reply with the code so we can verify you.",
     "answer": 0, "why": "That code (OTP) is a key to your account. Never share it."},
    {"from": "SMS from your cousin's new number", "msg": "Salam, this is my new number. I am stuck, please send Rs 10,000 to this account now.",
     "answer": 2, "why": "Call your cousin on the old number first. Scammers copy family."},
]
