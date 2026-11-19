# 🇺🇿 Kirill <-> Yangi & Klassik Lotin Telegram Boti

Ushbu Telegram bot o'zbek tilidagi har qanday **matn** va **hujjat fayllarini** (Word, PDF, Excel, PowerPoint, Text) quyidagi alifbolar o'rtasida to'liq va aniq o'girib beradi:

1. **Kirill alifbosi** (Ўзбекистон, шаҳар, чироқ)
2. **Yangi O'zbek Lotin alifbosi (2026-yilgi Qonun):**
   - **Oʻ oʻ** $\rightarrow$ **Ö ö** (*Özbekiston*)
   - **Gʻ gʻ** $\rightarrow$ **Ğ ğ** (*Toğ, Ğalaba*)
   - **Sh sh** $\rightarrow$ **Ş ş** (*Şahar, başlanğıç*)
   - **Ch ch** $\rightarrow$ **Ç ç** (*Çiroq, içimlik*)
3. **Klassik Lotin alifbosi** (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch)

---

## 🌟 Asosiy imkoniyatlar

- **🔄 Avtomatik aniqlash:** Yuborilgan matn yoki fayl yozuvini aniqlab, darhol o'giradi.
- **🆕 Yangi alifboga o'tkazish:** Eski lotindagi yoki kirilldagi har qanday matn va faylni 2026-yilgi yangi harflar (**Ö, Ğ, Ş, Ç**) bilan qayta yozib beradi.
- **🔀 Eski va Yangi Lotin o'rtasida konvertatsiya:** Mavjud eski hujjatlarni yangi alifboga yoki aksincha o'girish.
- **📄 Hujjatlarni qo'llab-quvvatlash:**
  - **Word (.docx):** Formatlar, jadvallar, rang va shriftlar saqlanadi.
  - **PDF (.pdf):** Matnni o'qib, o'girilgan yangi **PDF** va **Word (.docx)** fayl qilib beradi.
  - **Excel (.xlsx):** Kataklar va varaq nomlarini o'giradi.
  - **PowerPoint (.pptx):** Slaydlar va jadvallarni o'giradi.
  - **Matnli (.txt, .srt, .csv va h.k.):** Kodirovkasini avtomatik aniqlaydi.
- **🔘 Bir bosishda o'zgartirish:** Xabar ostidagi tugmalar orqali istalgan matnni bir zumda Yangi Lotin, Eski Lotin yoki Kirillga o'tkazish mumkin.

---

## 🚀 Ishga tushirish

1. **Tokenni kiritish:**
   [config.py](file:///c:/Users/Xurshidbek/ботга/config.py) faylini oching va [@BotFather](https://t.me/BotFather) dan olgan tokeningizni yozing:
   ```python
   BOT_TOKEN = "1234567890:AAH_sizning_tokeningiz"
   ```

2. **Botni ishga tushirish:**
   - [run_bot.bat](file:///c:/Users/Xurshidbek/ботга/run_bot.bat) faylini ikki marta bosing yoki terminalda:
   ```powershell
   python bot.py
   ```

---

## 📁 Loyiha tarkibi
- [bot.py](file:///c:/Users/Xurshidbek/ботга/bot.py) — Botning boshqaruv markazi va handlerlar.
- [translit.py](file:///c:/Users/Xurshidbek/ботга/translit.py) — Yangi Lotin, Klassik Lotin va Kirill transliteratsiyasi dvigateli.
- [file_handler.py](file:///c:/Users/Xurshidbek/ботга/file_handler.py) — Barcha turdagi fayllarni konvertatsiya qilish moduli.
- [config.py](file:///c:/Users/Xurshidbek/ботга/config.py) — Sozlamalar va token.
- [run_bot.bat](file:///c:/Users/Xurshidbek/ботга/run_bot.bat) — Windows da botni ishga tushirish skripti.
