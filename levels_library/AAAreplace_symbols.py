#!/usr/bin/env python3
"""
Преобразует all_microban.txt согласно MAPPING.

Правила:
  * символы из MAPPING — заменяются на значение из MAPPING;
  * символы НЕ из MAPPING — удаляются;
  * пустая строка / строка только из '_' — считается разделителем
    уровней и остаётся одной '_' (иначе уровни склеятся);
  * пробелы в конце строк обрезаются (padding в Sokoban-файлах).

Перед записью создаётся резервная копия: all_microban.txt.bak
"""
from pathlib import Path
import shutil
import sys

INPUT  = "all_microbanIII.txt"
OUTPUT = "all_microbanIII_custom.txt"        # можно поменять на другое имя
BACKUP_SUFFIX = ".bak"

MAPPING = {
    '#': '#',   # стена
    ' ': '_',   # пол
    '@': 'P',   # игрок
    '$': 'B',   # ящик
    '.': 'X',   # цель
    '*': 'G',   # ящик на цели
    '+': 'Q',   # игрок на цели
}


def process_line(line: str) -> str:
    line = line.rstrip(" ")                     # убираем padding справа
    s = line.strip()
    if not s or set(s) <= {"_"}:                # пустая или только '_'
        return "_"                              # -> разделитель
    # заменяем по MAPPING, всё остальное выкидываем
    return "".join(MAPPING[c] for c in line if c in MAPPING)


def main() -> None:
    src = Path(INPUT)
    if not src.exists():
        sys.exit(f"Файл не найден: {INPUT}")

    lines = src.read_text(encoding="utf-8").splitlines()

    # Диагностика: какие символы во входе не покрыты MAPPING
    unmapped: dict[str, int] = {}
    for line in lines:
        for c in line:
            if c not in MAPPING and c not in ("_", " ") and c.isprintable():
                unmapped[c] = unmapped.get(c, 0) + 1

    out_lines = [process_line(line) for line in lines]
    # склеиваем подряд идущие разделители в один (убираем пустые блоки)
    cleaned: list[str] = []
    for l in out_lines:
        if l == "_" and (not cleaned or cleaned[-1] == "_"):
            continue
        if not l:
            continue
        cleaned.append(l)
    # если не осталось финального разделителя — не критично
    while cleaned and cleaned[-1] == "_":
        cleaned.pop()

    dst = Path(OUTPUT)
    if dst.resolve() == src.resolve():
        shutil.copyfile(src, str(src) + BACKUP_SUFFIX)
        print(f"Бэкап: {src}{BACKUP_SUFFIX}")

    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(cleaned) + "\n")

    print(f"Готово: {dst}")
    print(f"Строк на входе:  {len(lines)}")
    print(f"Строк на выходе: {len(cleaned)}")
    print(f"Уровней: {sum(1 for l in cleaned if l == '_') + 1}")

    if unmapped:
        print("\nСимволы, которых не было в MAPPING (удалены):")
        for c, n in sorted(unmapped.items(), key=lambda kv: -kv[1]):
            print(f"  {c!r}: {n}")


if __name__ == "__main__":
    main()