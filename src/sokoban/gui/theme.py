import json
import os
from PIL import Image, ImageTk

# папка sokoban (на уровень выше gui)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_THEME_DIR = os.path.join(BASE_DIR, "textures", "default")
TEXTURES_DIR = os.path.join(BASE_DIR, "textures")

def list_themes():
    """Названия папок внутри textures (каждая папка это тема)."""
    if not os.path.isdir(TEXTURES_DIR):
        return []
    return sorted(name for name in os.listdir(TEXTURES_DIR)
                  if os.path.isdir(os.path.join(TEXTURES_DIR, name))
                  and not name.startswith((".", "__")))


# символ матрицы -> имя текстуры
SYMBOL_TO_NAME = {
    "#": "wall",
    "_": "floor",
    "B": "box",
    "X": "goal",
    "G": "box_on_goal",
    "P": "player",
    "Q": "player_on_goal",
    "?": "unknown",
}

# запасные цвета, если нет ни текстуры, ни записи в theme.json
DEFAULT_COLORS = {
    "wall": "#5b5b5b",
    "floor": "#e8e0c8",
    "box": "#b5792f",
    "goal": "#e8c547",
    "box_on_goal": "#6aa84f",
    "player": "#3d85c6",
    "player_on_goal": "#3d85c6",
    "outside": "#1e1e1e",
    "unknown": "#cc0000",
}

DEFAULT_UI = {
    "window_bg": "#2b2b2b",
    "panel_bg": "#3a3a3a",
    "button_bg": "#4a4a4a",
    "button_fg": "#ffffff",
    "grid_line": "#222222",
    "error_outline": "#ff3333",
}


class Theme:
    """Тема оформления: текстуры клеток + цвета интерфейса.
    Тема это папка с PNG-файлами (wall.png, floor.png, ...) и необязательным theme.json.
    Недостающие текстуры заменяются цветными квадратами."""

    def __init__(self, folder=DEFAULT_THEME_DIR):
        self.folder = folder
        self.colors = dict(DEFAULT_COLORS)
        self.ui = dict(DEFAULT_UI)
        self._source = {}   # name -> PIL.Image (RGBA) или None
        self._cache = {}    # (name, size) -> ImageTk.PhotoImage
        self._load_json()

    def _load_json(self):
        path = os.path.join(self.folder, "theme.json")
        if not os.path.isfile(path):
            return
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.colors.update(data.get("cells", {}))
        self.ui.update(data.get("ui", {}))

    def _load_source(self, name):
        """Читает PNG один раз. Возвращает RGBA-картинку или None."""
        if name in self._source:
            return self._source[name]
        img = None
        path = os.path.join(self.folder, name + ".png")
        if os.path.isfile(path):
            img = Image.open(path).convert("RGBA")
        self._source[name] = img
        return img

    def _compose(self, name):
        """Составные клетки: если нет готовой текстуры, накладываем
        коробку/игрока на цель."""
        base = self._load_source(name)
        if base is not None:
            return base
        overlay = {"box_on_goal": "box", "player_on_goal": "player"}.get(name)
        if overlay is None:
            return None
        goal, top = self._load_source("goal"), self._load_source(overlay)
        if goal is None or top is None:
            return None
        top = top.resize(goal.size, Image.NEAREST)
        return Image.alpha_composite(goal, top)

    def get_image(self, symbol, size):
        """PhotoImage нужного размера или None, если текстуры нет.
        Ссылки хранятся в кэше, иначе tkinter их «потеряет»."""
        name = SYMBOL_TO_NAME.get(symbol, "unknown")
        key = (name, size)
        if key in self._cache:
            return self._cache[key]
        src = self._compose(name)
        photo = None
        if src is not None:
            photo = ImageTk.PhotoImage(src.resize((size, size), Image.NEAREST))
        self._cache[key] = photo
        return photo

    def get_color(self, symbol):
        return self.colors[SYMBOL_TO_NAME.get(symbol, "unknown")]

    def clear_cache(self):
        """Вызывать при смене размера клетки, чтобы не копить старые картинки."""
        self._cache.clear()