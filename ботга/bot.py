"""
Kirill <-> Lotin Telegram Boti (Asosiy dastur).
YANGI TAHRIRDAGI O'ZBEK LOTIN ALIFBOSI (Ö ö, Ğ ğ, Ş ş, Ç ç) hamda
KLASSIK ALIFBO (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch) bo'yicha matn va barcha fayllarni
(Word, PDF, Excel, PowerPoint, Text) o'giruvchi to'liq tizim.
"""

import os
import sys
import uuid
import shutil
import logging
import telebot
from telebot import types

import config
from translit import (
    auto_transliterate,
    cyrillic_to_latin,
    latin_to_cyrillic,
    classic_to_new_latin,
    new_to_classic_latin,
    detect_script
)
from file_handler import convert_any_file

# Loglashni sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token tekshiruvi
token = config.BOT_TOKEN.strip()
if not token or token == "BOT_TOKENINGIZNI_SHU_YERGA_YOZING" or ":" not in token:
    print("\n" + "=" * 65)
    print("❌ DIQQAT: Telegram Bot Token kiritilmagan yoki noto'g'ri!")
    print("Iltimos, bot ishga tushishi uchun quyidagi qadamlarni bajaring:")
    print("1. Telegramda @BotFather ga kiring va bot ochib token oling.")
    print("2. 'config.py' faylini ochib, 'BOT_TOKEN' ga tokeningizni yozing.")
    print("   (yoki loyiha papkasida .env fayl yaratib: BOT_TOKEN=token_shu_yerda)")
    print("=" * 65 + "\n")
    sys.exit(1)

bot = telebot.TeleBot(token, parse_mode="HTML")

# Foydalanuvchilarning tanlagan rejimlari
user_modes = {}


def get_user_mode(user_id: int) -> str:
    return user_modes.get(user_id, 'auto')


def set_user_mode(user_id: int, mode: str):
    user_modes[user_id] = mode


# Asosiy tugmalar (ReplyKeyboardMarkup)
def get_main_keyboard(user_id: int):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    current_mode = get_user_mode(user_id)

    def check(mode_name):
        return " ✅" if current_mode == mode_name else ""

    btn_auto = f"🔄 Avto aniqlash{check('auto')}"
    btn_new_lat = f"🆕 Kirill ➡️ Yangi Lotin{check('new_latin')}"
    btn_classic_lat = f"🇺🇿 Kirill ➡️ Klassik Lotin{check('classic_latin')}"
    btn_cyr = f"📝 Lotin ➡️ Kirill{check('cyrillic')}"
    btn_c2n = f"🔀 Eski ➡️ Yangi Lotin{check('classic_to_new')}"
    btn_n2c = f"🔀 Yangi ➡️ Eski Lotin{check('new_to_classic')}"
    btn_help = "ℹ️ Yordam / Qo'llanma"

    markup.row(types.KeyboardButton(btn_auto))
    markup.row(types.KeyboardButton(btn_new_lat), types.KeyboardButton(btn_classic_lat))
    markup.row(types.KeyboardButton(btn_cyr))
    markup.row(types.KeyboardButton(btn_c2n), types.KeyboardButton(btn_n2c))
    markup.row(types.KeyboardButton(btn_help))
    return markup


# Inline tugmalar (har bir matn ostida tezkor almashtirish uchun)
def get_inline_transform_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_rev = types.InlineKeyboardButton("🔄 Teskarisiga", callback_data="act_reverse")
    btn_to_new = types.InlineKeyboardButton("🆕 Yangi Lotin (Ö,Ğ,Ş,Ç)", callback_data="act_to_new")
    btn_to_classic = types.InlineKeyboardButton("🇺🇿 Eski Lotin (Oʻ,Gʻ)", callback_data="act_to_classic")
    btn_to_cyr = types.InlineKeyboardButton("📝 Kirillga", callback_data="act_to_cyr")
    markup.add(btn_rev)
    markup.add(btn_to_new, btn_to_classic)
    markup.add(btn_to_cyr)
    return markup


@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    """
    /start buyrug'i
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Foydalanuvchi"

    welcome_text = (
        f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
        f"🤖 Ushbu bot matn va fayllarni quyidagi alifbolar o'rtasida mukammal o'giradi:\n\n"
        f"1️⃣ <b>Kirill yozuvi</b> (Ўзбекистон, шаҳар, чироқ)\n"
        f"2️⃣ <b>Yangi Lotin alifbosi (2026):</b> <code>Ö ö, Ğ ğ, Ş ş, Ç ç</code> (Özbekiston, şahar, çiroq)\n"
        f"3️⃣ <b>Klassik Lotin alifbosi:</b> <code>Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch</code>\n\n"
        f"📂 <b>Qo'llab-quvvatlanadigan fayllar:</b>\n"
        f"• 📄 Word (<code>.docx</code>), 📕 PDF (<code>.pdf</code>)\n"
        f"• 📊 Excel (<code>.xlsx</code>), 📑 PowerPoint (<code>.pptx</code>)\n"
        f"• 📝 Matnli fayllar (<code>.txt, .srt, .csv</code> va h.k.)\n\n"
        f"✍️ <i>Shunchaki xohlagan matningizni yozing yoki fayl yuboring!</i>"
    )

    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        reply_markup=get_main_keyboard(user_id)
    )


@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text and "Yordam / Qo'llanma" in msg.text)
def handle_help(message: types.Message):
    """
    /help yoki Yordam tugmasi
    """
    help_text = (
        "💡 <b>Botdan foydalanish bo'yicha yo'riqnoma:</b>\n\n"
        "🟢 <b>Yangi o'zbek alifbosi haqida:</b>\n"
        "2026-yilgi rasmiy qonunga asosan 4 ta harf yangilandi:\n"
        "• <b>Oʻ oʻ</b> ➡️ <b>Ö ö</b> (<i>Özbekiston</i>)\n"
        "• <b>Gʻ gʻ</b> ➡️ <b>Ğ ğ</b> (<i>Toğ</i>)\n"
        "• <b>Sh sh</b> ➡️ <b>Ş ş</b> (<i>Şahar</i>)\n"
        "• <b>Ch ch</b> ➡️ <b>Ç ç</b> (<i>Çiroq</i>)\n\n"
        "🔘 <b>Mavjud rejimlar:</b>\n"
        "• <b>🔄 Avto aniqlash:</b> Kirill kelsa Yangi Lotinga, Lotin kelsa Kirillga o'giradi.\n"
        "• <b>🆕 Kirill ➡️ Yangi Lotin:</b> Yangi harflar (Ö, Ğ, Ş, Ç) bilan yozadi.\n"
        "• <b>🇺🇿 Kirill ➡️ Klassik Lotin:</b> Eski (Oʻ, Gʻ, Sh, Ch) harflar bilan yozadi.\n"
        "• <b>📝 Lotin ➡️ Kirill:</b> Ham yangi, ham eski lotin yozuvini Kirillga o'giradi.\n"
        "• <b>🔀 Eski ➡️ Yangi Lotin:</b> Mavjud eski lotindagi matn/hujjatni yangi alifboga o'tkazadi.\n"
        "• <b>🔀 Yangi ➡️ Eski Lotin:</b> Yangi alifbodan eski lotinga qaytaradi.\n\n"
        "Kerakli rejimni pastdagi tugmalar orqali tanlang."
    )
    bot.send_message(
        chat_id=message.chat.id,
        text=help_text,
        reply_markup=get_main_keyboard(message.from_user.id)
    )


@bot.message_handler(func=lambda msg: msg.text and any(k in msg.text for k in [
    "Avto aniqlash", "Kirill ➡️ Yangi Lotin", "Kirill ➡️ Klassik Lotin",
    "Lotin ➡️ Kirill", "Eski ➡️ Yangi Lotin", "Yangi ➡️ Eski Lotin"
]))
def handle_mode_switch(message: types.Message):
    """
    Menyu orqali rejimni almashtirish
    """
    text = message.text
    user_id = message.from_user.id

    if "Avto aniqlash" in text:
        set_user_mode(user_id, 'auto')
        status = "✅ Rejim: <b>🔄 Avto aniqlash</b> (Kirill ➡️ Yangi Lotin, Lotin ➡️ Kirill)"
    elif "Kirill ➡️ Yangi Lotin" in text:
        set_user_mode(user_id, 'new_latin')
        status = "✅ Rejim: <b>🆕 Kirill ➡️ Yangi Lotin</b> (Ö ö, Ğ ğ, Ş ş, Ç ç)"
    elif "Kirill ➡️ Klassik Lotin" in text:
        set_user_mode(user_id, 'classic_latin')
        status = "✅ Rejim: <b>🇺🇿 Kirill ➡️ Klassik Lotin</b> (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch)"
    elif "Lotin ➡️ Kirill" in text:
        set_user_mode(user_id, 'cyrillic')
        status = "✅ Rejim: <b>📝 Lotin ➡️ Kirill</b> (barcha lotincha matnlar kirillga)"
    elif "Eski ➡️ Yangi Lotin" in text:
        set_user_mode(user_id, 'classic_to_new')
        status = "✅ Rejim: <b>🔀 Eski Lotin ➡️ Yangi Lotin</b> (Oʻ,Gʻ,Sh,Ch ➡️ Ö,Ğ,Ş,Ç)"
    elif "Yangi ➡️ Eski Lotin" in text:
        set_user_mode(user_id, 'new_to_classic')
        status = "✅ Rejim: <b>🔀 Yangi Lotin ➡️ Eski Lotin</b> (Ö,Ğ,Ş,Ç ➡️ Oʻ,Gʻ,Sh,Ch)"
    else:
        status = "Rejim tanlandi."

    bot.send_message(
        chat_id=message.chat.id,
        text=status,
        reply_markup=get_main_keyboard(user_id)
    )


@bot.message_handler(content_types=['text'])
def handle_text_message(message: types.Message):
    """
    Oddiy matn xabarlarini o'girish
    """
    text = message.text
    if not text:
        return

    user_id = message.from_user.id
    mode = get_user_mode(user_id)

    # O'girish
    converted_text, src_script, dst_script = auto_transliterate(
        text,
        target_script=mode,
        latin_version=config.DEFAULT_LATIN_VERSION
    )

    # Agar matn juda uzun bo'lsa (Telegram 4096 cheklovi)
    if len(converted_text) > 4000:
        temp_dir = os.path.join(config.TEMP_DIR, f"text_{user_id}_{uuid.uuid4().hex[:6]}")
        os.makedirs(temp_dir, exist_ok=True)
        txt_file_path = os.path.join(temp_dir, f"ugirilgan_{dst_script.lower().replace(' ', '_')}.txt")

        try:
            with open(txt_file_path, "w", encoding="utf-8") as f:
                f.write(converted_text)

            caption = (
                f"✅ <b>Matn o'girildi!</b>\n"
                f"🔤 <b>Yo'nalish:</b> {src_script} ➡️ {dst_script}\n"
                f"ℹ️ Matn juda uzun bo'lgani sababli fayl shaklida yuborildi."
            )
            with open(txt_file_path, "rb") as doc:
                bot.send_document(
                    chat_id=message.chat.id,
                    document=doc,
                    caption=caption,
                    reply_to_message_id=message.message_id
                )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        bot.reply_to(
            message=message,
            text=converted_text,
            reply_markup=get_inline_transform_markup()
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("act_"))
def handle_inline_actions(call: types.CallbackQuery):
    """
    Inline tugmalar bosilganda matnni xohlagan alifboga o'zgartirish
    """
    orig_text = call.message.text
    if not orig_text:
        bot.answer_callback_query(call.id, "Matn topilmadi!")
        return

    action = call.data
    new_text = orig_text
    info = ""

    if action == "act_reverse":
        current = detect_script(orig_text)
        if current == 'cyrillic':
            new_text = cyrillic_to_latin(orig_text, alphabet_version='new')
            info = "Yangi Lotinga o'girildi"
        else:
            new_text = latin_to_cyrillic(orig_text)
            info = "Kirillga o'girildi"

    elif action == "act_to_new":
        current = detect_script(orig_text)
        if current == 'cyrillic':
            new_text = cyrillic_to_latin(orig_text, alphabet_version='new')
        else:
            new_text = classic_to_new_latin(orig_text)
        info = "Yangi Lotinga (Ö, Ğ, Ş, Ç) o'girildi"

    elif action == "act_to_classic":
        current = detect_script(orig_text)
        if current == 'cyrillic':
            new_text = cyrillic_to_latin(orig_text, alphabet_version='classic')
        else:
            new_text = new_to_classic_latin(orig_text)
        info = "Klassik Lotinga (Oʻ, Gʻ) o'girildi"

    elif action == "act_to_cyr":
        new_text = latin_to_cyrillic(orig_text)
        info = "Kirillga o'girildi"

    if new_text == orig_text:
        bot.answer_callback_query(call.id, "Matn allaqachon shu ko'rinishda.")
        return

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=new_text,
            reply_markup=get_inline_transform_markup()
        )
        bot.answer_callback_query(call.id, f"✅ {info}!")
    except Exception:
        bot.answer_callback_query(call.id, "O'zgartirildi.")


@bot.message_handler(content_types=['document'])
def handle_document_message(message: types.Message):
    """
    Fayl (PDF, Word, Excel, PPTX, TXT va h.k.) yuborilganda
    """
    document = message.document
    file_name = document.file_name or "hujjat.docx"
    file_size = document.file_size or 0

    if file_size > config.MAX_FILE_SIZE_BYTES:
        bot.reply_to(
            message,
            f"❌ <b>Fayl hajmi juda katta!</b>\n"
            f"Telegram Bot API orqali faqat <b>{config.MAX_FILE_SIZE_MB} MB</b> gacha bo'lgan "
            f"fayllarni qabul qila olaman. Fayl hajmi: {round(file_size / (1024 * 1024), 2)} MB."
        )
        return

    status_msg = bot.reply_to(
        message,
        f"⏳ <b>'{file_name}'</b> fayli qabul qilindi.\n"
        f"Yuklab olinmoqda va o'girilmoqda, iltimos kuting..."
    )

    user_id = message.from_user.id
    mode = get_user_mode(user_id)

    session_id = uuid.uuid4().hex[:8]
    work_dir = os.path.join(config.TEMP_DIR, f"{user_id}_{session_id}")
    input_file_path = os.path.join(work_dir, file_name)
    output_dir = os.path.join(work_dir, "output")

    os.makedirs(work_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Faylni yuklab olish
        file_info = bot.get_file(document.file_id)
        downloaded_data = bot.download_file(file_info.file_path)

        with open(input_file_path, "wb") as f:
            f.write(downloaded_data)

        # Faylni o'girish
        generated_files, direction = convert_any_file(
            input_path=input_file_path,
            output_dir=output_dir,
            original_filename=file_name,
            mode=mode
        )

        if not generated_files:
            raise ValueError("O'girilgan fayl yaratilmadi.")

        # Foydalanuvchiga yuborish
        for out_path in generated_files:
            out_name = os.path.basename(out_path)
            caption = (
                f"✅ <b>Fayl muvaffaqiyatli o'girildi!</b>\n"
                f"📁 <b>Nomi:</b> <code>{out_name}</code>\n"
                f"🔤 <b>Yo'nalish:</b> {direction}"
            )
            with open(out_path, "rb") as doc:
                bot.send_document(
                    chat_id=message.chat.id,
                    document=doc,
                    caption=caption,
                    reply_to_message_id=message.message_id
                )

        try:
            bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

    except ValueError as ve:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"⚠️ <b>Ogohlantirish:</b> {str(ve)}"
        )
    except Exception as e:
        logger.error(f"Fayl o'girishda xatolik: {e}", exc_info=True)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=f"❌ <b>Xatolik:</b> Faylni qayta ishlab bo'lmadi.\n<i>Tafsilot: {str(e)[:100]}</i>"
        )
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@bot.message_handler(content_types=['audio', 'voice', 'video', 'photo', 'sticker'])
def handle_other_contents(message: types.Message):
    bot.reply_to(
        message,
        "ℹ️ Iltimos, <b>matn</b> yoki <b>hujjat fayli</b> (Word .docx, PDF, Excel, Matn .txt) yuboring."
    )


def start_render_health_server():
    """
    Render.com bepul Web Service talabi: $PORT da HTTP server ishlab turishi shart.
    Agar PORT mavjud bo'lsa (Renderda avtomatik beriladi), fonda yengil HTTP server ochiladi.
    """
    port_str = os.getenv("PORT")
    if port_str:
        try:
            port = int(port_str)
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import threading

            class HealthHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Bot Render serverida muvaffaqiyatli ishlab turibdi!")

                def log_message(self, format, *args):
                    pass

            server = HTTPServer(("0.0.0.0", port), HealthHandler)
            srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
            srv_thread.start()
            logger.info(f"Render uchun Web Server {port}-portda ishga tushirildi.")
        except Exception as e:
            logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")


def main():
    print("=" * 65)
    print("🤖 Kirill <-> Yangi & Klassik Lotin Telegram Boti ishga tushmoqda...")
    print("Botni to'xtatish uchun Ctrl + C tugmalarini bosing.")
    print("=" * 65)

    # Render.com yoki boshqa serverlar uchun portni ochish
    start_render_health_server()

    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=20)
    except (KeyboardInterrupt, SystemExit):
        print("\nBot to'xtatildi.")
    except Exception as e:
        logger.critical(f"Bot to'xtab qoldi: {e}", exc_info=True)


if __name__ == "__main__":
    main()
