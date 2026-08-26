"""Localise the premade characters: names inside .gcd and the .bio text.

The .gcd name is a 32-byte null-padded field at 0x174. The .bio is CP1251
text with CRLF endings, rendered in a narrow fixed box on the character
creation screen, so lines are kept within the original 27-column budget.
"""
import os, sys

LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
PRE = os.path.join(LH, 'data', 'premade')
NAME_OFF, NAME_LEN = 0x174, 0x20
MAX_COL = 27

NAMES = {
    'COMBAT.GCD': 'Джошуа',
    'STEALTH.GCD': 'Мерфи',
    'diplomat.gcd': 'Эбигейл',
}

BIOS = {
    'combat.bio': """
Номер субъекта: B2331

Место содержания:
- Исправительный блок,
  сектор "А"
Личные данные:
- Возраст: 34
- Пол: мужской
 Найден в секторе D5,
 тяжелая потеря памяти
- Восстановление: 24 мес.
- Дата выхода: 22.02.2321
Дополнительно:
- Основные навыки: базовая
  боевая подготовка;
  холодное, метательное
  и легкое стрелковое.
- Прочее: общение,
  первая помощь,
  выживание.
""",
    'DIPLOMAT.BIO': """
Номер субъекта: B2813

Место содержания:
- Исправительный блок,
  сектор "А"
Личные данные:
- Возраст: 23
- Пол: женский
 Найдена в секторе D5,
 тяжелая форма амнезии
- Восстановление: 5 мес.
- Дата выхода: 22.02.2321
Дополнительно:
- Основные навыки: азы
  рукопашного боя,
  опытный дипломат,
  научный склад ума.
- Характер: избегает
  конфликтов. Склонна
  все усложнять.
""",
    'STEALTH.BIO': """
Номер субъекта: B2018

Место содержания:
- Исправительный блок,
  сектор "А"
Личные данные:
- Возраст: 28
- Пол: мужской
 Найден в секторе D5,
 тяжелая форма ПТСР
- Восстановление: 24 мес.
- Дата выхода: 22.02.2321
Дополнительно:
- Основные навыки: азы
  боевой подготовки.
  Хитер и незаметен.
- Заключение психиатра:
  нет эмпатии, выраженный
  синдром героя, возможно
  употребление химии.
""",
}


def find(name):
    for fn in os.listdir(PRE):
        if fn.lower() == name.lower():
            return os.path.join(PRE, fn)
    return None


ok = True
for fn, name in NAMES.items():
    p = find(fn)
    enc = name.encode('cp1251')
    assert len(enc) < NAME_LEN, fn
    with open(p, 'rb') as f:
        b = bytearray(f.read())
    old = bytes(b[NAME_OFF:NAME_OFF + NAME_LEN]).split(b'\x00')[0].decode('cp1251')
    b[NAME_OFF:NAME_OFF + NAME_LEN] = enc + b'\x00' * (NAME_LEN - len(enc))
    with open(p, 'wb') as f:
        f.write(bytes(b))
    print(f'{fn:<16} {old!r} -> {name!r}')

print()
for fn, text in BIOS.items():
    p = find(fn)
    lines = text.replace('\r\n', '\n').split('\n')
    # strip the single leading newline the triple-quote introduces
    if lines and lines[0] == '':
        lines = lines[1:]
    if lines and lines[-1] == '':
        lines = lines[:-1]
    # the original bios open with a blank line, which sets where the text
    # sits vertically in the character-creation box; keep that spacing
    lines = [''] + lines
    over = [(i, len(l), l) for i, l in enumerate(lines) if len(l) > MAX_COL]
    for i, n, l in over:
        print(f'  !! {fn} line {i}: {n} cols > {MAX_COL}: {l!r}')
        ok = False
    blob = '\r\n'.join(lines).encode('cp1251')
    with open(p, 'wb') as f:
        f.write(blob)
    print(f'{fn:<16} {len(lines)} lines, max {max(len(l) for l in lines)} cols')

print('\nOK' if ok else '\nWIDTH PROBLEMS')
