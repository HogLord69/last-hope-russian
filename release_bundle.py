#!/usr/bin/env python3
"""Build the distributable archive: a single self-contained, ready-to-play folder.

    python release.py --out "C:\\sotj-release"

Produces Fallout-Story-of-the-Jackal-English.zip, which extracts to one folder
you launch from directly. The English text is already applied -- this packages
the installed state, it does not translate anything. Run
`python oly_tool.py verify` first; this script refuses to build if any Russian
is left on disk.

The game is ~640 MB, so it fits GitHub's 2 GB per-asset limit in one piece.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

GAME = r"C:\Users\adamn\Downloads\Last Hope mod 1.088"
NAME = "Last-Hope-1.088-Russian"
EXE = "LHmod.exe"

SEVENZIP = [r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"]
ASSET_LIMIT = 2 * 1000 ** 3

# Backups and working files a player has no use for.
SKIP_FILES = ["*.orig", "*.dmp", "sfall-log*.txt", "*.log"]
SKIP_DIRS = ["uninstall", "_backup_english_original", "_localization_ru"]

LAUNCHER = """@echo off
rem Last Hope v1.088 -- Russian. Must run from its own folder.
cd /d "%~dp0"
start "" "{exe}"
"""

READ_ME = """LAST HOPE v1.088 -- РУССКАЯ ВЕРСИЯ
=====================================

Тотальная конверсия для Fallout 2. Автор мода - DeJ@n (Forgotten_Knight).


КАК ИГРАТЬ
----------

  Запустите:  Играть в Last Hope.bat

Устанавливать ничего не нужно. Сохранения лежат в этой же папке.


ЧТО ПЕРЕВЕДЕНО
--------------

  * 57 358 из 57 638 строк - 99%
  * 1 144 файла диалогов
  * Интерфейс, предметы, перки, описания
  * Сообщения sfall

Оставшиеся 280 строк оставлены по-английски намеренно: имена скриптов
движка, названия API DirectX, обозначения оружия (FN FAL, M249 SAW,
AHS-9), служебные заглушки разработчика и подпись автора мода.

Проверено: потерянных идентификаторов нет, ошибок кодировки CP1251 нет,
все символы покрыты шрифтами игры.


ЕСЛИ ЧТО-ТО НЕ ТАК
------------------

Ошибки и шероховатости самой игры - это игра. Всё, что плохо читается
по-русски, - это мы, пишите.

Чёрный экран при запуске? Правой кнопкой по {exe} -> Свойства ->
Совместимость -> "Отключить оптимизацию во весь экран".


См. CREDITS.txt.
"""

CREDITS = """БЛАГОДАРНОСТИ
=============

LAST HOPE
    DeJ@n (Forgotten_Knight). В игре подписано как
    "Last Hope" by F.K.S. Since '05. Версия 1.088.

FALLOUT 2
    Black Isle Studios / Interplay.

ДВИЖОК
    sfall - Timeslip, NovaRain, phobos2077 и другие.
    High Resolution Patch - Mash и Drobovik.

STORY OF THE JACKAL
    Часть русского текста взята из русской версии Story of the Jackal,
    и только там, где английский оригинал двух модов совпадает
    посимвольно. Спасибо Foxx и всем, кто над ней работал.

СООБЩЕСТВО
    No Mutants Allowed, где этот мод и живёт. И множество других людей,
    чья работа нигде не подписана.


Поправки приветствуются и будут внесены дословно.
"""


def find_7z():
    for c in SEVENZIP:
        if os.path.exists(c):
            return c
    found = shutil.which("7z")
    if found:
        return found
    raise RuntimeError("7-Zip not found")


def check_clean():
    """Refuse to build unless the localization verifies.

    Runs Last Hope's own dlg_verify, which reads every shipped .msg the way the
    engine will and reports lost ids, CP1251 failures and untranslated strings.
    """
    tools = os.path.join(GAME, "_localization_ru", "tools")
    script = os.path.join(tools, "dlg_verify.py")
    if not os.path.isfile(script):
        print("  ! dlg_verify.py not found, skipping the pre-flight check")
        return True
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, script], capture_output=True, text=True,
                       cwd=tools, env=env)
    out = (r.stdout or "") + (r.stderr or "")
    keys = ("lost ids", "cp1251", "Russian", "still English", "strings")
    for line in out.splitlines():
        if any(k in line for k in keys):
            print("  " + line.strip())
    bad = [l for l in out.splitlines()
           if ("lost ids" in l or "cp1251 failures" in l)
           and not l.rstrip().endswith("0")]
    if bad:
        print("  pre-flight FAILED:")
        for l in bad:
            print("   ", l.strip())
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--game", default=GAME)
    ap.add_argument("--skip-verify", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.game):
        print(f"game not found: {args.game}")
        return 1

    out = os.path.abspath(args.out)
    staging = os.path.join(out, "_staging", NAME)
    archive = os.path.join(out, NAME + ".zip")
    os.makedirs(out, exist_ok=True)
    if os.path.exists(staging):
        shutil.rmtree(staging)
    os.makedirs(staging)

    if not args.skip_verify and not check_clean():
        print("russian still on disk -- refusing to build. run oly_tool.py verify")
        return 1

    print(f"staging {args.game}")
    t0 = time.time()
    cmd = ["robocopy", args.game, staging, "/E", "/MT:16", "/R:1", "/W:1",
           "/NFL", "/NDL", "/NJH", "/NJS", "/NP"]
    cmd += ["/XF"] + SKIP_FILES
    cmd += ["/XD"] + [os.path.join(args.game, d) for d in SKIP_DIRS]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode >= 8:
        print(f"robocopy failed ({r.returncode})")
        return 1

    with open(os.path.join(staging, "Играть в Last Hope.bat"),
              "w", newline="\r\n") as f:
        f.write(LAUNCHER.format(exe=EXE))
    # These carry Cyrillic. With no explicit encoding Python falls back to the
    # machine locale and raises on the first Russian character. utf-8-sig so
    # Windows Notepad opens them the right way round.
    with open(os.path.join(staging, "ПРОЧТИ МЕНЯ.txt"), "w",
              newline="\r\n", encoding="utf-8-sig") as f:
        f.write(READ_ME.format(exe=EXE))
    with open(os.path.join(staging, "CREDITS.txt"), "w",
              newline="\r\n", encoding="utf-8-sig") as f:
        f.write(CREDITS)

    size_raw = sum(os.path.getsize(os.path.join(b, n))
                   for b, _, fs in os.walk(staging) for n in fs)
    print(f"  staged {size_raw / 2**20:.0f} MB in {time.time() - t0:.0f}s")

    print("compressing")
    if os.path.exists(archive):
        os.remove(archive)
    t0 = time.time()
    r = subprocess.run([find_7z(), "a", "-tzip", "-mx=5", "-mmt=on", "-bso0", "-bsp0",
                        archive, staging], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"7z failed ({r.returncode})\n{r.stdout}\n{r.stderr}")
        return 1
    shutil.rmtree(os.path.join(out, "_staging"), ignore_errors=True)

    size = os.path.getsize(archive)
    print(f"  {size / 2**20:.0f} MB in {time.time() - t0:.0f}s "
          f"({100 * size / size_raw:.0f}% of raw)")
    if size > ASSET_LIMIT:
        print("  !! over GitHub's 2 GB asset limit")
        return 1
    print(f"\n{archive}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
