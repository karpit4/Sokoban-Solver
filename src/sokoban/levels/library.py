"""Библиотека уровней: папка levels_library, один уровень в одном .txt файле.
Название уровня это имя файла без расширения."""
import os
import random
import re

from levels.loaders import parse_txt
from paths import LIBRARY_DIR


def _natural_key(name):
    """level2 раньше level10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name.lower())]


def list_names():
    """Названия всех уровней в библиотеке."""
    if not os.path.isdir(LIBRARY_DIR):
        return []
    names = [os.path.splitext(f)[0] for f in os.listdir(LIBRARY_DIR)
             if f.lower().endswith(".txt")]
    return sorted(names, key=_natural_key)


def find(query):
    """Названия, содержащие query (без учёта регистра). Пустой запрос возвращает все."""
    query = query.strip().lower()
    return [name for name in list_names() if query in name.lower()]


def load(name):
    """Матрица уровня по названию.
    ValueError, если файла нет, в нём недопустимые символы или не ровно один уровень."""
    path = os.path.join(LIBRARY_DIR, name + ".txt")
    if not os.path.isfile(path):
        raise ValueError(f'Уровня "{name}" нет в библиотеке')
    levels = parse_txt(path)
    if len(levels) != 1:
        raise ValueError(f'В файле "{name}.txt" должен быть один уровень, найдено: {len(levels)}')
    return levels[0]


def random_name():
    """Название случайного уровня или None, если библиотека пуста."""
    names = list_names()
    return random.choice(names) if names else None