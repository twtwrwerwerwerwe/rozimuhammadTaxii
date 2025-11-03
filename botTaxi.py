# -*- coding: utf-8 -*-
import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat

# =================== TELEGRAM API ===================
api_id = 28023612
api_hash = 'fe94ef46addc1b6b8253d5448e8511f0'

# Telegram session nomi
client = TelegramClient('taxi_session', api_id, api_hash)

# E’lonlar yuboriladigan kanal/guruh
TARGET_CHAT = 'https://t.me/+BFl15wH-PAswZTYy'

# =================== KALIT SO'ZLAR ===================
KEYWORDS = [
    # odam bor
    'odam bor','odambor','odam bor ekan','odam bor edi','odam borakan',
    'bitta odam bor','ikkita odam bor','uchta odam bor',"to'rtta odam bor",'tortta odam bor',
    'komplek odam bor','komplekt odam bor','kompilek odam bor','kampilek odam bor',
    '1ta odam bor','2ta odam bor','3ta odam bor','4ta odam bor',
    'odam bor 1','odam bor 2','odam bor 3','odam bor 4',
    'rishtonga odam bor','toshkentga odam bor',"toshkendan farg'onaga odam bor",
    'тўрта одам бор','одам бор','комплект одам бор','компилект odam бор','кампилек одам бор',

    # mashina kerak
    'mashina kerak','mashina kere','mashina kerek','mashina kera','mashina keraa',
    'bagajli mashina kerak','bosh mashina kerak','bosh mashina bormi','boshi bormi',
    'mashina izlayapman','mashina topaman','mashina kerak edi',
    'машина керак','багажли машина керак','бош машина керак','машина кере','машina кераа',

    # pochta bor
    'pochta bor','pochta kerak','pochta ketadi','pochta olib ketadi','pochta bormi',
    'почта бор','почта кетади','почта керак','почта олиб кетади',
    'тошкентга почта бор','тошкентдан почта бор','риштонга почта бор','риштондан почта бор',

    # ketadi
    'ketadi','ketvotti','ketayapti','ketishadi','ketishi kerak','hozir ketadi',
    'кетяпт','кетвотди','кетади','кетишади','кетиши керак',

    # dostavka
    'dastavka bor','dostavka bor','dastafka','dastafka bor',
    'доставкa бор','даставка бор','доставка бор','доставкa керак'
]

KEYWORDS_RE = re.compile("|".join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)

# Telefon raqam regex
PHONE_RE = re.compile(r'(\+?998[\d\-\s\(\)]{9,15}|9\d{8})')

# =================== FUNKSIYALAR ===================
def normalize_phone(raw):
    digits = re.sub(r'\D', '', raw)
    if digits.startswith('998') and len(digits) >= 12:
        return '+' + digits[:12]
    if len(digits) == 9 and digits.startswith('9'):
        return '+998' + digits
    if len(digits) == 10 and digits.startswith('0'):
        return '+998' + digits[1:]
    if len(digits) >= 9:
        return '+998' + digits[-9:]
    return None

# =================== HANDLER ===================
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        # Faqat guruh/kanal xabarlarini tekshir
        if not isinstance(event.peer_id, (PeerChannel, PeerChat)):
            return

        text = event.raw_text
        if not text or not KEYWORDS_RE.search(text):
            return

        # Chat va sender ma'lumotlarini olish
        chat_task = asyncio.create_task(event.get_chat())
        sender_task = asyncio.create_task(event.get_sender())
        chat, sender = await asyncio.gather(chat_task, sender_task)

        # Guruh nomi va link
        group_name = getattr(chat, 'title', 'Noma\'lum guruh')
        if getattr(chat, 'username', None):
            group_link = f"https://t.me/{chat.username}/{event.id}"
        else:
            group_link = group_name

        # Habar egasi
        username = getattr(sender, 'username', None)
        if username:
            haber_egasi = f"@{username}"
        else:
            haber_egasi = "Berkitilgan"

        # Maxsus profil link
        sender_id = getattr(sender, 'id', None)
        if sender_id:
            profile_link_html = f"<a href='tg://user?id={sender_id}'>Profilga o‘tish</a>"
        else:
            profile_link_html = "Berkitilgan"

        # Telefon raqam
        phone = getattr(sender, 'phone', None)
        if phone:
            phone = normalize_phone(phone)
        else:
            # Matndan qidiring
            for m in PHONE_RE.finditer(text):
                phone = normalize_phone(m.group(0))
                if phone:
                    break
        phone_display = phone if phone else "Raqam berkitilgan"

        # Xabarni shakllantirish
        message_text = (
            f"🚖 <b>Xabar topildi!</b>\n\n"
            f"📄 <b>Matn:</b>\n{text}\n\n"
            f"📍 <b>Guruh:</b> {group_name} — {group_link}\n\n"
            f"👤 <b>Habar egasi:</b> {haber_egasi}\n\n"
            f"📞 <b>Raqam:</b> {phone_display}\n\n"
            f"🔗 <b>Maxsus link:</b> {profile_link_html}\n\n"
            f"🔔 Yangi e’lonlardan xabardor bo‘ling!"
        )

        # Yuborish
        await client.send_message(TARGET_CHAT, message_text, parse_mode='html')
        print(f"✅ Yuborildi: {text[:50]}...")

    except Exception as e:
        print("❌ Xatolik:", e)

# =================== START ===================
print("🚕 Taxi bot ishga tushdi... Faqat yangi xabarlar tez tekshiriladi ⚡")
client.start()
client.run_until_disconnected()
