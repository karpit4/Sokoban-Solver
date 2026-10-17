#!/usr/bin/env python3
"""
Удаляет все ФАЙЛЫ в текущей папке, имя которых начинается с 'microban'.
Папки (даже с таким именем) не трогает.
"""
from pathlib import Path

PREFIX = "microban"

targets = [
    p for p in Path(".").iterdir()
    if p.is_file() and p.name.startswith(PREFIX)
]

if not targets:
    print("Нечего удалять — файлов с таким префиксом нет.")
else:
    print(f"Будет удалено файлов: {len(targets)}")
    for p in sorted(targets):
        print(f"  {p.name}")
    answer = input("Удалить? [y/N] ").strip().lower()
    if answer != "y":
        print("Отменено.")
        raise SystemExit(0)

    deleted = 0
    for p in targets:
        try:
            p.unlink()
            deleted += 1
        except OSError as e:
            print(f"  ! не удалось удалить {p.name}: {e}")
    print(f"\nУдалено: {deleted} из {len(targets)}")