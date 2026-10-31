"""Scam Dojo ke pehle se likhe messages (6 scam, 5 asli).

Yeh tab kaam aate hain jab GEMINI_API_KEY na ho ya internet na ho.
Har highlight ka 'phrase' message ke text mein hu-ba-hu maujood hona chahiye.
kind: "red" = red flag, "green" = achi nishani.
"""

SCAM = [
    {
        "id": "f-jazz",
        "channel": "SMS",
        "sender": "JazzCash",
        "text": "JazzCash Alert: Aap ka account 24 ghantay mein BLOCK ho jayega. Abhi verify karein: http://jazzcash-verify.top/login aur apna PIN likhein.",
        "is_scam": True,
        "headline": "Jaldi ka dabao, nakli link aur PIN ki maang.",
        "highlights": [
            {"phrase": "24 ghantay mein BLOCK ho jayega", "kind": "red", "why": "Scammer jaldi machate hain taake aap sochein nahi."},
            {"phrase": "http://jazzcash-verify.top/login", "kind": "red", "why": "Asli JazzCash ka link aisa nahi hota. Yeh nakli website hai."},
            {"phrase": "apna PIN likhein", "kind": "red", "why": "PIN koi company kabhi nahi maangti."},
        ],
        "seedhi_baat": "Yeh JazzCash ka message nahi, chor ka hai. Woh aap ka PIN churana chahta hai.",
        "kya_karein": "Link par click na karein, PIN na bataein. Message delete karein aur PTA ko report karein.",
    },
    {
        "id": "f-bisp",
        "channel": "WhatsApp",
        "sender": "+92 312 5550123",
        "text": "Mubarak! BISP Ehsaas se aap ke liye Rs 25,000 manzoor hue hain. Paisay lene ke liye apna CNIC aur OTP is number par bhejein: 0312-5550123",
        "is_scam": True,
        "headline": "Inaam ka lalach aur OTP ki maang.",
        "highlights": [
            {"phrase": "Rs 25,000 manzoor hue hain", "kind": "red", "why": "Bina form bhare ya bina SMS 8171 check kiye paisay nahi milte. Yeh lalach hai."},
            {"phrase": "apna CNIC aur OTP", "kind": "red", "why": "CNIC aur OTP dono se chor aap ka account khol sakta hai."},
            {"phrase": "is number par bhejein", "kind": "red", "why": "Sarkari idaray WhatsApp number par code nahi mangtay."},
        ],
        "seedhi_baat": "Yeh BISP ka message nahi hai. Koi bhi sarkari idara OTP nahi poochta.",
        "kya_karein": "Jawab na dein. Number block karein. BISP ki baat sirf official 8171 service ya daftar se confirm karein.",
    },
    {
        "id": "f-otp",
        "channel": "SMS",
        "sender": "+92 345 7770099",
        "text": "Bhai galti se mere Rs 15,000 aap ke Easypaisa mein aa gaye hain. Abhi 6 digit ka code aaya hoga, wo bata dein, main paisay wapas le lun.",
        "is_scam": True,
        "headline": "Galti se paisay bhejne ka bahana, asal mein OTP chahiye.",
        "highlights": [
            {"phrase": "galti se mere Rs 15,000", "kind": "red", "why": "Yeh purani chaal hai. Asal mein koi paisay nahi aaye hote."},
            {"phrase": "6 digit ka code", "kind": "red", "why": "Yeh aap ka OTP hai. Isse chor aap ke account se paisay nikaal leta hai."},
            {"phrase": "bata dein", "kind": "red", "why": "Code kisi ko bhi batana mana hai, chahe wo kitna hi shareef lage."},
        ],
        "seedhi_baat": "Koi paisay nahi aaye. Chor aap ka OTP maang raha hai.",
        "kya_karein": "Code kabhi na bataein. Apna balance khud app mein dekhein. Number block karein.",
    },
    {
        "id": "f-parcel",
        "channel": "SMS",
        "sender": "TCS-Info",
        "text": "TCS: Aap ka parcel address ghalat hone ki wajah se ruka hai. Rs 150 fee dein warna wapas bhej diya jayega: tcs-pk-delivery.xyz",
        "is_scam": True,
        "headline": "Parcel ke naam par nakli fee aur nakli link.",
        "highlights": [
            {"phrase": "Rs 150 fee dein", "kind": "red", "why": "Chhoti raqam isliye maangte hain ke aap card ki detail de dein."},
            {"phrase": "warna wapas bhej diya jayega", "kind": "red", "why": "Dhamki aur jaldi, dono scam ki nishaniyan hain."},
            {"phrase": "tcs-pk-delivery.xyz", "kind": "red", "why": "Courier company ka asli link aisa nahi hota."},
        ],
        "seedhi_baat": "Yeh courier ka message nahi, nakli link hai jo aap ka card chura sakta hai.",
        "kya_karein": "Link na kholein. Agar parcel ka intezar hai to company ki official app ya helpline se tracking dekhein.",
    },
    {
        "id": "f-job",
        "channel": "WhatsApp",
        "sender": "+92 300 1234500",
        "text": "Ghar baithay kamayein Rs 5,000 rozana! Sirf Rs 2,000 registration fee Easypaisa karein. Seats limited hain, aaj hi!",
        "is_scam": True,
        "headline": "Aasan kamai ka wada aur pehle fee ki maang.",
        "highlights": [
            {"phrase": "Rs 5,000 rozana", "kind": "red", "why": "Bina mehnat ya skill ke itni kamai ka wada jhoota hota hai."},
            {"phrase": "Rs 2,000 registration fee", "kind": "red", "why": "Asli naukri mein pehle paisay nahi liye jate."},
            {"phrase": "Seats limited hain, aaj hi!", "kind": "red", "why": "Jaldi karwane ki chaal."},
        ],
        "seedhi_baat": "Asli naukri paisay deke nahi milti. Yeh log fee le kar ghayab ho jate hain.",
        "kya_karein": "Paisay na bhejein. Number block karein. Naukri sirf jaani pehchani company ki website se dhoondein.",
    },
    {
        "id": "f-family",
        "channel": "WhatsApp",
        "sender": "+92 333 9871234",
        "text": "Assalam o alaikum, main aap ka beta bol raha hun, mera phone toot gaya, ye mera naya number hai. Abhi Rs 10,000 JazzCash karo, bohat zaroori hai, kisi ko mat batana.",
        "is_scam": True,
        "headline": "Beta ban kar paisay maangna, aur raaz rakhne ko kehna.",
        "highlights": [
            {"phrase": "ye mera naya number hai", "kind": "red", "why": "Ghar wale ka naya number achanak aana shak ki baat hai."},
            {"phrase": "Abhi Rs 10,000 JazzCash karo", "kind": "red", "why": "Paisay fauran maangna jaldi ka dabao hai."},
            {"phrase": "kisi ko mat batana", "kind": "red", "why": "Chor chahta hai ke koi aap ko rok na sake."},
        ],
        "seedhi_baat": "Yeh aap ka beta nahi, koi chor hai. Woh ghar walon ki shakal ka bahana banata hai.",
        "kya_karein": "Paisay na bhejein. Beta ko purane number par call karein ya ghar ke kisi se poochein.",
    },
]

REAL = [
    {
        "id": "f-bank",
        "channel": "SMS",
        "sender": "HBL",
        "text": "HBL: Rs 2,500 aap ke account se ATM se nikalay gaye. Baqi balance Rs 18,340. Agar yeh aap ne nahi kiya to card ke peeche likhe helpline number par call karein.",
        "is_scam": False,
        "headline": "Sirf maloomat deta hai, kuch maangta nahi.",
        "highlights": [
            {"phrase": "Rs 2,500 aap ke account se ATM se nikalay gaye", "kind": "green", "why": "Yeh sirf transaction ki khabar hai."},
            {"phrase": "card ke peeche likhe helpline number", "kind": "green", "why": "Bank apna asli helpline batata hai, koi anjaan number ya link nahi."},
        ],
        "seedhi_baat": "Yeh normal bank alert lagta hai. Is mein PIN, OTP ya link nahi maanga gaya.",
        "kya_karein": "Agar nikasi aap ne ki thi to koi masla nahi. Agar nahi, to card ke peeche wale number par call karein.",
    },
    {
        "id": "f-ammi",
        "channel": "WhatsApp",
        "sender": "Ammi",
        "text": "Beta, aaj shaam ko khana ghar par khana, Khala aa rahi hain. Raste mein doodh le aana.",
        "is_scam": False,
        "headline": "Jaana pehchana banda, paisay ya link ki baat nahi.",
        "highlights": [
            {"phrase": "Beta, aaj shaam ko khana ghar par khana", "kind": "green", "why": "Ghar ki aam si baat, koi dabao nahi."},
            {"phrase": "Raste mein doodh le aana", "kind": "green", "why": "Koi paisay, code ya link nahi maanga gaya."},
        ],
        "seedhi_baat": "Yeh Ammi ka aam sa message hai. Shak ki koi wajah nahi.",
        "kya_karein": "Jawab de dein. Agar number naya ho to pehle call kar ke pakka kar lein.",
    },
    {
        "id": "f-clinic",
        "channel": "SMS",
        "sender": "Shifa Clinic",
        "text": "Shifa Clinic: Kal subah 10:00 baje Dr. Saira ke saath aap ka appointment hai. Tabdeeli ke liye clinic ke number par call karein.",
        "is_scam": False,
        "headline": "Appointment ki yaad dahani, kuch maanga nahi gaya.",
        "highlights": [
            {"phrase": "Kal subah 10:00 baje", "kind": "green", "why": "Saaf waqt aur tareekh, koi jaldi ka dabao nahi."},
            {"phrase": "clinic ke number par call karein", "kind": "green", "why": "Aap ko wohi number use karna hai jo aap ke paas pehle se hai."},
        ],
        "seedhi_baat": "Yeh asli reminder lagta hai agar aap ne appointment li thi.",
        "kya_karein": "Agar appointment aap ne li thi to waqt par chale jayein. Warna clinic ko khud call kar ke poochein.",
    },
    {
        "id": "f-package",
        "channel": "SMS",
        "sender": "Jazz",
        "text": "Jazz: Aap ka weekly internet package kal khatam ho raha hai. Dobara lene ke liye Jazz ki official app kholein.",
        "is_scam": False,
        "headline": "Official app ka kehta hai, link ya PIN nahi maangta.",
        "highlights": [
            {"phrase": "kal khatam ho raha hai", "kind": "green", "why": "Sirf khabar hai, dhamki nahi."},
            {"phrase": "Jazz ki official app kholein", "kind": "green", "why": "Apni app kholne ko kaha, anjaan link par jane ko nahi."},
        ],
        "seedhi_baat": "Normal company reminder lagta hai.",
        "kya_karein": "Chahein to apni app se dekh lein. Is message mein koi khatra nahi.",
    },
    {
        "id": "f-daraz",
        "channel": "SMS",
        "sender": "Daraz",
        "text": "Daraz: Aap ka order #84213 kal tak pohanch jayega. Rider ko sirf order number dikhayein. Hum aap se kabhi PIN ya OTP nahi maangte.",
        "is_scam": False,
        "headline": "Saaf batata hai ke PIN ya OTP nahi maanga jayega.",
        "highlights": [
            {"phrase": "order #84213", "kind": "green", "why": "Aap ke apne order ka number hai. Aap app mein check kar sakte hain."},
            {"phrase": "Hum aap se kabhi PIN ya OTP nahi maangte", "kind": "green", "why": "Asli company khud aap ko hoshiyar karti hai."},
        ],
        "seedhi_baat": "Agar aap ne Daraz se order kiya hai to yeh asli lagta hai.",
        "kya_karein": "Order number app mein mila lein. Agar aap ne order nahi kiya tha to ignore karein.",
    },
]
