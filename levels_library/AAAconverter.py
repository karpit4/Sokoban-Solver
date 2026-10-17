#!/usr/bin/env python3
"""
Разбивает all_microban.txt на microbanIII1.txt, microbanIII2.txt, ...

Разделитель уровня = строка, состоящая ТОЛЬКО из символов '_'
(одного или нескольких):  '_', '__', '___' и т.д.

Подряд идущие разделители схлопываются (пустые уровни не создаются).
Ведущие/хвостовые пустые строки уровня обрезаются.
"""
import re
import sys
from pathlib import Path

INPUT  = "all_microbanIII_custom.txt"
PREFIX = "microbanIII"

SEP_RE = re.compile(r"^_+$")


def main() -> None:
    src = Path(INPUT)
    if not src.exists():
        sys.exit(f"Файл не найден: {INPUT}")

    # utf-8-sig — на случай BOM в начале файла
    lines = src.read_text(encoding="utf-8-sig").splitlines()

    levels: list[list[str]] = []
    current: list[str] = []

    def flush() -> None:
        # обрезаем пустые строки сверху/снизу
        while current and not current[0].strip():
            current.pop(0)
        while current and not current[-1].strip():
            current.pop()
        if current:
            levels.append(current[:])

    for line in lines:
        if SEP_RE.match(line.strip()):
            flush()
            current.clear()
        else:
            current.append(line)
    flush()

    if not levels:
        sys.exit("Уровней не найдено — проверь разделители.")

    for i, lvl in enumerate(levels, 1):
        fname = f"{PREFIX}{i}.txt"
        with open(fname, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lvl) + "\n")
        print(f"written {fname}  ({len(lvl)} строк)")

    print(f"\nГотово: {len(levels)} уровней "
          f"-> {PREFIX}1.txt ... {PREFIX}{len(levels)}.txt")


if __name__ == "__main__":
    main()