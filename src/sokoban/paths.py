import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # src\sokoban
PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))  # Sokoban

TEXTURES_DIR = os.path.join(BASE_DIR, "textures")
DEFAULT_THEME_DIR = os.path.join(TEXTURES_DIR, "default")

LEVELS_DIR = os.path.join(PROJECT_DIR, "levels")           # сохранённые уровни
TRAINING_DIR = os.path.join(PROJECT_DIR, "training")       # скриншоты для бенчмарка
BENCHMARKS_DIR = os.path.join(PROJECT_DIR, "benchmarks")   # результаты бенчмарка

LIBRARY_DIR = os.path.join(PROJECT_DIR, "levels_library")  # библиотека уровней для игры