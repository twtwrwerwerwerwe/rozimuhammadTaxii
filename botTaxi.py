# -*- coding: utf-8 -*-
import re
import asyncio
import hashlib
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel, PeerChat

# =================== TELEGRAM API ===================
api_id = 28023612
api_hash = 'fe94ef46addc1b6b8253d5448e8511f0'

# Sessiya nomi (serverda yangi sessiya yaratadi)
client = TelegramClient('taxi_ultrafast_session', api_id, api_hash)

# =================== TARGET CHAT ===================
TARGET_CHAT = 'https://t.me/+BFl15wH-PAswZTYy'

# =================== KALIT SO'ZLAR ===================
KEYWORDS = [
    # Odam bor
    'odam bor', 'odambor', 'odam bor ekan', 'odam bor edi', 'odam borakan',
    'bitta odam bor', 'ikkita odam bor', 'uchta odam bor', "to'rtta odam bor", 'tortta odam bor',
    'komplek odam bor', 'komplekt odam bor', 'kompilek odam bor', 'kampilek odam bor',
    '1ta odam bor', '2ta odam bor', '3ta odam bor', '4ta odam bor',
    'odam bor 1', 'odam bor 2', 'odam bor 3', 'odam bor 4',
    'rishtonga odam bor', 'toshkentga odam bor', "toshkendan farg'onaga odam bor",
    'тўрта одам бор', 'одам бор', 'комплект одам бор', 'компилект odam бор', 'кампилек одам бор',

    # Mashina kerak
    'mashina kerak', 'mashina kere', 'mashina kerek', 'mashina kera', 'mashina keraa',
    'bagajli mashina kerak', 'bosh mashina kerak', 'bosh mashina bormi', 'boshi bormi',
    'mashina izlayapman', 'mashina topaman', 'mashina kerak edi',
    'машина керак', 'багажли машина керак', 'бош машина керак', 'машина кере', 'машина кераа',

    # Pochta bor
    'pochta bor', 'pochta kerak', 'pochta ketadi', 'pochta olib ketadi', 'pochta bormi',
    'почта бор', 'почта кетади', 'почта керак', 'почта олиб кетади',
    'тошкентга почта бор', 'тошкентдан почта бор', 'риштонга почта бор', 'риштондан почта бор',

    # Ketadi
    'ketadi', 'ketvotti', 'ketayapti', 'ketishadi', 'ketishi kerak', 'hozir ketadi',
    'кетяпт', 'кетвотди', 'кетади', 'кетишади', 'кетиши керак',

    # Dostavka
    'dastavka bor', 'dostavka bor', 'dastafka', 'dastafka bor',
    'доставкa бор', 'даставка бор', 'доставка бор', 'доставкa керак'
]

# Regex bilan birlashtiramiz
KEYWORDS_RE = re.compile(r"|".join(re.escape(k) for k in KEYWORDS), re.IGNORECASE)

# =================== TELEFON RAQAM ===================
PHONE_RE = re.compile(r'(\+?998[\d]{9}|0\d{9}|9\d{8})')

def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r'\D', '', raw)
    if not digits:
        return None
    if digits.startswith('998') and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith('9') and len(digits) == 9:
        return f"+998{digits}"
    if digits.startswith('0') and len(digits) == 10:
        return f"+998{digits[1:]}"
    return None

# =================== DUPLICATE XABAR TEKSHIRISH ===================
seen_hashes = set()

def get_md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# =================== ASOSIY HANDLER ===================
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        # Faqat guruh/kanal xabarlari
        if not isinstance(event.peer_id, (PeerChannel, PeerChat)):
            return

        text = event.raw_text or ""
        if not text.strip():
            return

        # Kalit so'zlar tekshiruvi
        if not KEYWORDS_RE.search(text):
            return

        # Duplicate tekshirish
        text_hash = get_md5(text)
        if text_hash in seen_hashes:
            return
        seen_hashes.add(text_hash)

        # Chat va sender
        chat_task = asyncio.create_task(event.get_chat())
        sender_task = asyncio.create_task(event.get_sender())
        chat, sender = await asyncio.gather(chat_task, sender_task)

        # Guruh nomi va link
        group_name = getattr(chat, 'title', "Noma'lum guruh")
        if getattr(chat, 'username', None):
            group_link = f"https://t.me/{chat.username}/{event.id}"
        else:
            group_link = group_name

        # Habar egasi
        username = getattr(sender, 'username', None)
        if username:
            haber_egasi = f"@{username}"
        else:
            haber_egasi = getattr(sender, 'first_name', "Berkitilgan")

        sender_id = getattr(sender, 'id', None)
        profile_link = f"<a href='tg://user?id={sender_id}'>Profilga o‘tish</a>" if sender_id else "Berkitilgan"

        # Telefon raqam
        phone = getattr(sender, 'phone', None)
        if phone:
            phone_norm = normalize_phone(str(phone))
        else:
            phone_norm = None
        if not phone_norm:
            for m in PHONE_RE.finditer(text):
                candidate = m.group(0)
                phone_norm = normalize_phone(candidate)
                if phone_norm:
                    break
        phone_display = phone_norm if phone_norm else "Raqam berkitilgan"

        # Xabar matni
        message_text = (
            f"🚖 <b>Xabar topildi!</b>\n\n"
            f"📄 <b>Matn:</b>\n{text}\n\n"
            f"📍 <b>Guruh:</b> {group_name} — {group_link}\n\n"
            f"👤 <b>Habar egasi:</b> {haber_egasi}\n\n"
            f"📞 <b>Raqam:</b> {phone_display}\n\n"
            f"🔗 <b>Maxsus link:</b> {profile_link}\n\n"
            f"🔔 Yangi e’lonlardan xabardor bo‘ling!"
        )

        await client.send_message(TARGET_CHAT, message_text, parse_mode='html')
        print(f"✅ Yuborildi: {group_name} | {haber_egasi} | {phone_display}")

    except Exception as e:
        print("❌ Xatolik:", e)

# =================== ISHGA TUSHIRISH ===================
print("🚕 ULTRA FAST Taxi Bot ishga tushdi...")
client.start()
client.run_until_disconnected()
