# Last Hope — русская локализация

Русский перевод **Last Hope v1.088**, тотальной конверсии для *Fallout 2*
за авторством DeJ@n (Forgotten_Knight).

Скачайте, распакуйте, запустите. Ничего устанавливать не нужно.

Готовая сборка — во вкладке **[Releases](../../releases)**.

**57 358 из 57 638 строк переведено — 99%.** Оставшиеся 280 оставлены
по-английски намеренно: имена скриптов движка, названия API DirectX,
обозначения оружия (FN FAL, M249 SAW, AHS-9), служебные заглушки
разработчика и подпись автора мода.

---

## Что переведено

| | Строк |
|---|---|
| Диалоги | 1 144 файла, 57 638 строк |
| Интерфейс и игровой текст | 19 901 строка |
| Сообщения sfall (`translations/russian.ini`) | — |

Проверено: потерянных идентификаторов нет, ошибок кодирования в CP1251 нет,
все символы покрыты шрифтами игры.

## Как это собрано

Порядок доверия к источникам, от высшего к низшему:

1. `overrides/` и `dlg_overrides/` — перевод, написанный вручную
2. Русский текст *Story of the Jackal* — только там, где английский оригинал
   Jackal посимвольно совпадает с английским оригиналом Last Hope
3. Английский текст Last Hope — оставлен как есть и отмечен как несделанный

Второй источник — не догадка: строка берётся только при точном совпадении
английского исходника, поэтому подстановка проверяема.

## Инструменты

```bash
python tools/build.py        собрать .msg из overrides
python tools/dlg_build.py    собрать диалоги
python tools/dlg_verify.py   проверить собранные диалоги
python tools/validate.py     проверить кодируемость в CP1251 и покрытие шрифтами
python tools/audit.py        что ещё осталось по-английски
```

Пути к игре заданы константами в начале каждого скрипта — поправьте их,
если игра стоит в другом месте.

Вывод — обычные файлы в `data/text/english/`, которые движок читает раньше
архива. **`master.dat` не перезаписывается.** Чтобы откатиться, удалите
эти файлы.

## Важное про движок

**Файл в `data/` заменяет файл из архива целиком, а не построчно.** Слияния
по идентификаторам не происходит. Поэтому правильный источник для каждого
файла — это английский файл из `data/`, если Last Hope его поставляет, и
только иначе — версия из архива. Сборка учитывает это.

---

# English

Russian localization for **Last Hope v1.088**, a *Fallout 2* total conversion
by DeJ@n (Forgotten_Knight).

**57,358 of 57,638 strings translated — 99%.** The remaining 280 are English
on purpose: engine script identifiers, DirectX API names, weapon designations,
developer placeholders, and the mod author's signature line.

Verified with the project's own tools — no lost string ids, no CP1251 encoding
failures, every character covered by the game's fonts.

This repository ships **the Russian text and the tooling only**. Last Hope
itself is not included, and neither is its English source text: the build
scripts read that from your own copy.

Ready-to-play archive in [Releases](../../releases). Credits in
[CREDITS.md](CREDITS.md).

## Licence

Tooling and the Russian text: MIT, see [LICENSE](LICENSE).

Last Hope belongs to its author. Nothing here grants any right to it.
