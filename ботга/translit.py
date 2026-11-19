"""
O'zbek tili uchun mukammal Kirill <-> Lotin transliteratsiya moduli.
2026-yilgi QONUN bilan tasdiqlangan YANGI TAHRIRDAGI O'ZBEK LOTIN ALIFBOSI
(Ö ö, Ğ ğ, Ş ş, Ç ç) hamda AMALDAGI (KLASSIK) ALIFBO (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch)
to'liq qo'llab-quvvatlanadi.
"""

import re

# Unli harflar to'plami
CYR_VOWELS = set('АЕЁИОУЭЮЯЎаеёиоуэюяў')
LAT_VOWELS = set('AEIOUÖaeiouö')

# Apostrof turlari: ' ‘ ’ ʻ ʼ `
APOSTROPHES = "'\u2018\u2019\u02bb\u02bc`"
APOSTR_REGEX_PART = "[" + re.escape(APOSTROPHES) + "]"

# Kirill -> Lotin yakka harflar (umumiy harflar)
CYR_TO_LAT_BASE = {
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x',
    'Ҳ': 'H', 'ҳ': 'h',
    'Қ': 'Q', 'қ': 'q',
    'Э': 'E', 'э': 'e',
    'ъ': "'", 'Ъ': "'",
    'ь': "",  'Ь': "",
}

# Lotin -> Kirill yakka harflar
LAT_TO_CYR_MAP = {
    'a': 'а', 'A': 'А',
    'b': 'б', 'B': 'Б',
    'd': 'д', 'D': 'Д',
    'f': 'ф', 'F': 'Ф',
    'g': 'г', 'G': 'Г',
    'h': 'ҳ', 'H': 'Ҳ',
    'i': 'и', 'I': 'И',
    'j': 'ж', 'J': 'Ж',
    'k': 'к', 'K': 'К',
    'l': 'л', 'L': 'Л',
    'm': 'м', 'M': 'М',
    'n': 'н', 'N': 'Н',
    'o': 'о', 'O': 'О',
    'p': 'п', 'P': 'П',
    'q': 'қ', 'Q': 'Қ',
    'r': 'р', 'R': 'Р',
    's': 'с', 'S': 'С',
    't': 'т', 'T': 'Т',
    'u': 'у', 'U': 'У',
    'v': 'в', 'V': 'В',
    'x': 'х', 'X': 'Х',
    'y': 'й', 'Y': 'Й',
    'z': 'з', 'Z': 'З',
    # Yangi alifbo harflari
    'ö': 'ў', 'Ö': 'Ў',
    'ğ': 'ғ', 'Ğ': 'Ғ',
    'ş': 'ш', 'Ş': 'Ш',
    'ç': 'ч', 'Ç': 'Ч',
}


def cyrillic_to_latin(text: str, alphabet_version: str = "new", apostrophe: str = "oʻ") -> str:
    """
    Kirill yozuvidagi matnni Lotin yozuviga o'giradi.
    
    alphabet_version:
      - 'new': 2026-yilgi yangi tahrir (Ö ö, Ğ ğ, Ş ş, Ç ç)
      - 'classic': Amaldagi tahrir (Oʻ oʻ, Gʻ gʻ, Sh sh, Ch ch)
      
    apostrophe:
      - 'oʻ' (standart oʻzbek harfi U+02BB)
      - 'o\'' (oddiy apostrof)
    """
    if not text:
        return ""

    is_new = (alphabet_version == "new")

    apo_char = "ʻ" if "ʻ" in apostrophe else "'"
    o_classic = "o" + apo_char
    O_classic = "O" + apo_char
    g_classic = "g" + apo_char
    G_classic = "G" + apo_char

    res = []
    length = len(text)

    for i, ch in enumerate(text):
        # 1. 'Е' va 'е' qoidasi
        if ch in ('Е', 'е'):
            is_start_or_vowel = (i == 0) or (text[i - 1] in CYR_VOWELS) or not text[i - 1].isalpha()
            next_is_upper = (i + 1 < length and text[i + 1].isupper())
            prev_is_upper = (i > 0 and text[i - 1].isupper())

            if ch == 'Е':
                if is_start_or_vowel:
                    res.append('YE' if (next_is_upper or prev_is_upper) else 'Ye')
                else:
                    res.append('E')
            else:
                res.append('ye' if is_start_or_vowel else 'e')

        # 2. Qo'shma harflar: Ё, Ю, Я, Ц
        elif ch in ('Ё', 'ё'):
            next_is_upper = (i + 1 < length and text[i + 1].isupper())
            prev_is_upper = (i > 0 and text[i - 1].isupper())
            res.append(('YO' if (next_is_upper or prev_is_upper) else 'Yo') if ch == 'Ё' else 'yo')

        elif ch in ('Ю', 'ю'):
            next_is_upper = (i + 1 < length and text[i + 1].isupper())
            prev_is_upper = (i > 0 and text[i - 1].isupper())
            res.append(('YU' if (next_is_upper or prev_is_upper) else 'Yu') if ch == 'Ю' else 'yu')

        elif ch in ('Я', 'я'):
            next_is_upper = (i + 1 < length and text[i + 1].isupper())
            prev_is_upper = (i > 0 and text[i - 1].isupper())
            res.append(('YA' if (next_is_upper or prev_is_upper) else 'Ya') if ch == 'Я' else 'ya')

        elif ch in ('Ц', 'ц'):
            next_is_upper = (i + 1 < length and text[i + 1].isupper())
            prev_is_upper = (i > 0 and text[i - 1].isupper())
            res.append(('TS' if (next_is_upper or prev_is_upper) else 'Ts') if ch == 'Ц' else 'ts')

        # 3. Ч / ч (Yangi alifboda: Ç / ç, Klassikda: Ch / ch)
        elif ch in ('Ч', 'ч'):
            if is_new:
                res.append('Ç' if ch == 'Ч' else 'ç')
            else:
                next_is_upper = (i + 1 < length and text[i + 1].isupper())
                prev_is_upper = (i > 0 and text[i - 1].isupper())
                res.append(('CH' if (next_is_upper or prev_is_upper) else 'Ch') if ch == 'Ч' else 'ch')

        # 4. Ш / ш, Щ / щ (Yangi alifboda: Ş / ş, Klassikda: Sh / sh)
        elif ch in ('Ш', 'ш', 'Щ', 'щ'):
            if is_new:
                res.append('Ş' if ch in ('Ш', 'Щ') else 'ş')
            else:
                next_is_upper = (i + 1 < length and text[i + 1].isupper())
                prev_is_upper = (i > 0 and text[i - 1].isupper())
                res.append(('SH' if (next_is_upper or prev_is_upper) else 'Sh') if ch in ('Ш', 'Щ') else 'sh')

        # 5. Ў / ў (Yangi alifboda: Ö / ö, Klassikda: Oʻ / oʻ)
        elif ch == 'Ў':
            if is_new:
                res.append('Ö')
            else:
                next_is_upper = (i + 1 < length and text[i + 1].isupper())
                prev_is_upper = (i > 0 and text[i - 1].isupper())
                res.append(O_classic.upper() if (next_is_upper or prev_is_upper) else O_classic)
        elif ch == 'ў':
            res.append('ö' if is_new else o_classic)

        # 6. Ғ / ғ (Yangi alifboda: Ğ / ğ, Klassikda: Gʻ / gʻ)
        elif ch == 'Ғ':
            if is_new:
                res.append('Ğ')
            else:
                next_is_upper = (i + 1 < length and text[i + 1].isupper())
                prev_is_upper = (i > 0 and text[i - 1].isupper())
                res.append(G_classic.upper() if (next_is_upper or prev_is_upper) else G_classic)
        elif ch == 'ғ':
            res.append('ğ' if is_new else g_classic)

        # 7. Tutuq belgisi (ъ, Ъ)
        elif ch in ('ъ', 'Ъ'):
            if res and res[-1].endswith(('ʻ', "'", '’', 'ʼ', '`')):
                continue
            res.append("'")

        # 8. Boshqa harflar
        elif ch in CYR_TO_LAT_BASE:
            res.append(CYR_TO_LAT_BASE[ch])
        else:
            res.append(ch)

    return ''.join(res)


def latin_to_cyrillic(text: str) -> str:
    """
    Lotin yozuvidagi matnni Kirill yozuviga o'giradi.
    HAM YANGI ALIFBO (Ö, Ğ, Ş, Ç), HAM KLASSIK (Oʻ, Gʻ, Sh, Ch) matnlarni
    avtomatik taniydi va to'liq o'giradi.
    """
    if not text:
        return ""

    t = text

    # 1. Multi-character klassik almashtirishlar (O', G', Sh, Ch, Yo, Yu, Ya, Ye, Ts)
    multi_patterns = [
        # O' va G' (har xil apostroflar bilan)
        (re.compile(r'O' + APOSTR_REGEX_PART, re.UNICODE), 'Ў'),
        (re.compile(r'o' + APOSTR_REGEX_PART, re.UNICODE), 'ў'),
        (re.compile(r'G' + APOSTR_REGEX_PART, re.UNICODE), 'Ғ'),
        (re.compile(r'g' + APOSTR_REGEX_PART, re.UNICODE), 'ғ'),

        # Sh, Ch
        (re.compile(r'SH\b', re.UNICODE), 'Ш'),
        (re.compile(r'SH(?=[A-Z])', re.UNICODE), 'Ш'),
        (re.compile(r'Sh', re.UNICODE), 'Ш'),
        (re.compile(r'sh', re.UNICODE), 'ш'),
        (re.compile(r'CH\b', re.UNICODE), 'Ч'),
        (re.compile(r'CH(?=[A-Z])', re.UNICODE), 'Ч'),
        (re.compile(r'Ch', re.UNICODE), 'Ч'),
        (re.compile(r'ch', re.UNICODE), 'ч'),

        # Yo, Yu, Ya, Ye, Ts
        (re.compile(r'YO\b', re.UNICODE), 'Ё'),
        (re.compile(r'YO(?=[A-Z])', re.UNICODE), 'Ё'),
        (re.compile(r'Yo', re.UNICODE), 'Ё'),
        (re.compile(r'yo', re.UNICODE), 'ё'),

        (re.compile(r'YU\b', re.UNICODE), 'Ю'),
        (re.compile(r'YU(?=[A-Z])', re.UNICODE), 'Ю'),
        (re.compile(r'Yu', re.UNICODE), 'Ю'),
        (re.compile(r'yu', re.UNICODE), 'ю'),

        (re.compile(r'YA\b', re.UNICODE), 'Я'),
        (re.compile(r'YA(?=[A-Z])', re.UNICODE), 'Я'),
        (re.compile(r'Ya', re.UNICODE), 'Я'),
        (re.compile(r'ya', re.UNICODE), 'я'),

        (re.compile(r'YE\b', re.UNICODE), 'Е'),
        (re.compile(r'YE(?=[A-Z])', re.UNICODE), 'Е'),
        (re.compile(r'Ye', re.UNICODE), 'Е'),
        (re.compile(r'ye', re.UNICODE), 'е'),

        (re.compile(r'TS\b', re.UNICODE), 'Ц'),
        (re.compile(r'TS(?=[A-Z])', re.UNICODE), 'Ц'),
        (re.compile(r'Ts', re.UNICODE), 'Ц'),
        (re.compile(r'ts', re.UNICODE), 'ц'),
    ]

    for pattern, repl in multi_patterns:
        t = pattern.sub(repl, t)

    # 2. 'E' va 'e' qoidasi
    t = re.sub(r'(^|[^a-zA-Zа-яА-ЯўЎғҒöÖğĞşŞçÇ])E', r'\1Э', t)
    t = re.sub(r'(^|[^a-zA-Zа-яА-ЯўЎғҒöÖğĞşŞçÇ])e', r'\1э', t)
    vowels_pattern = r'([AaIiOoUuÖöАаИиОоУуЎўЭэЕе])'
    t = re.sub(vowels_pattern + r'E', r'\1Э', t)
    t = re.sub(vowels_pattern + r'e', r'\1э', t)
    t = t.replace('E', 'Е').replace('e', 'е')

    # 3. So'z ichidagi tutuq belgisi (apostrof): masalan, a'lo -> аъло, ma'lumot -> маълумот
    t = re.sub(r'([a-zA-Zа-яА-ЯўЎғҒöÖğĞşŞçÇ])' + APOSTR_REGEX_PART + r'([a-zA-Zа-яА-ЯўЎғҒöÖğĞşŞçÇ])', r'\1ъ\2', t)

    # 4. Yakka harflarni o'girish (yangi alifbodagi Ö, Ğ, Ş, Ç ham LAT_TO_CYR_MAP ichida bor)
    res = []
    for ch in t:
        if ch in LAT_TO_CYR_MAP:
            res.append(LAT_TO_CYR_MAP[ch])
        else:
            res.append(ch)

    return ''.join(res)


def classic_to_new_latin(text: str) -> str:
    """
    Amaldagi klassik Lotin (Oʻ, Gʻ, Sh, Ch) yozuvini
    2026-yilgi Yangi Lotin (Ö, Ğ, Ş, Ç) yozuviga o'giradi.
    """
    if not text:
        return ""

    t = text

    # Oʻ -> Ö, oʻ -> ö
    t = re.sub(r'O' + APOSTR_REGEX_PART, 'Ö', t)
    t = re.sub(r'o' + APOSTR_REGEX_PART, 'ö', t)

    # Gʻ -> Ğ, gʻ -> ğ
    t = re.sub(r'G' + APOSTR_REGEX_PART, 'Ğ', t)
    t = re.sub(r'g' + APOSTR_REGEX_PART, 'ğ', t)

    # Sh -> Ş, sh -> ş
    t = re.sub(r'SH\b', 'Ş', t)
    t = re.sub(r'SH(?=[A-Z])', 'Ş', t)
    t = re.sub(r'Sh', 'Ş', t)
    t = re.sub(r'sh', 'ş', t)

    # Ch -> Ç, ch -> ç
    t = re.sub(r'CH\b', 'Ç', t)
    t = re.sub(r'CH(?=[A-Z])', 'Ç', t)
    t = re.sub(r'Ch', 'Ç', t)
    t = re.sub(r'ch', 'ç', t)

    return t


def new_to_classic_latin(text: str, apostrophe: str = "oʻ") -> str:
    """
    2026-yilgi Yangi Lotin (Ö, Ğ, Ş, Ç) yozuvini
    Amaldagi klassik Lotin (Oʻ, Gʻ, Sh, Ch) yozuviga o'giradi.
    """
    if not text:
        return ""

    apo = "ʻ" if "ʻ" in apostrophe else "'"
    o_char = "o" + apo
    O_char = "O" + apo
    g_char = "g" + apo
    G_char = "G" + apo

    replacements = {
        'Ö': O_char,
        'ö': o_char,
        'Ğ': G_char,
        'ğ': g_char,
        'Ş': 'Sh',
        'ş': 'sh',
        'Ç': 'Ch',
        'ç': 'ch',
    }

    res = []
    for ch in text:
        res.append(replacements.get(ch, ch))
    return ''.join(res)


def detect_script(text: str) -> str:
    """
    Matn qaysi alifboda ekanini aniqlaydi:
    - 'cyrillic': Kirill
    - 'new_latin': Yangi Lotin (Ö, Ğ, Ş, Ç harflari mavjud)
    - 'latin': Klassik/umumiy Lotin
    """
    if not text:
        return 'latin'

    cyr_count = 0
    lat_count = 0
    new_lat_count = 0

    for ch in text:
        if ('\u0400' <= ch <= '\u04FF') or ch in 'ўЎғҒқҚҳҲ':
            cyr_count += 1
        elif ch in 'öÖğĞşŞçÇ':
            new_lat_count += 1
            lat_count += 1
        elif ('a' <= ch <= 'z') or ('A' <= 'Z'):
            lat_count += 1

    if cyr_count >= lat_count and cyr_count > 0:
        return 'cyrillic'
    elif new_lat_count > 0:
        return 'new_latin'
    else:
        return 'latin'


def auto_transliterate(text: str, target_script: str = 'auto', latin_version: str = 'new') -> tuple[str, str, str]:
    """
    Matnni o'giradi.
    target_script:
      - 'auto': avtomatik aniqlaydi
      - 'new_latin': Kirill yoki Eski Lotin -> Yangi Lotin (Ö, Ğ, Ş, Ç)
      - 'classic_latin': Kirill yoki Yangi Lotin -> Eski Lotin (Oʻ, Gʻ, Sh, Ch)
      - 'cyrillic': Yangi yoki Eski Lotin -> Kirill
      - 'classic_to_new': Eski Lotin -> Yangi Lotin
      - 'new_to_classic': Yangi Lotin -> Eski Lotin
    """
    if target_script == 'new_latin':
        current = detect_script(text)
        if current == 'cyrillic':
            return cyrillic_to_latin(text, alphabet_version="new"), 'Kirill', 'Yangi Lotin'
        else:
            return classic_to_new_latin(text), 'Eski Lotin', 'Yangi Lotin'

    elif target_script == 'classic_latin':
        current = detect_script(text)
        if current == 'cyrillic':
            return cyrillic_to_latin(text, alphabet_version="classic"), 'Kirill', 'Eski Lotin'
        else:
            return new_to_classic_latin(text), 'Yangi Lotin', 'Eski Lotin'

    elif target_script == 'cyrillic':
        return latin_to_cyrillic(text), 'Lotin', 'Kirill'

    elif target_script == 'classic_to_new':
        return classic_to_new_latin(text), 'Eski Lotin', 'Yangi Lotin'

    elif target_script == 'new_to_classic':
        return new_to_classic_latin(text), 'Yangi Lotin', 'Eski Lotin'

    else:
        # Avtomatik aniqlash
        current = detect_script(text)
        if current == 'cyrillic':
            if latin_version == 'new':
                return cyrillic_to_latin(text, alphabet_version="new"), 'Kirill', 'Yangi Lotin'
            else:
                return cyrillic_to_latin(text, alphabet_version="classic"), 'Kirill', 'Eski Lotin'
        else:
            # Lotin (yangi yoki klassik) -> Kirill
            src = 'Yangi Lotin' if current == 'new_latin' else 'Lotin'
            return latin_to_cyrillic(text), src, 'Kirill'
