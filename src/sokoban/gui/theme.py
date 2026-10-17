import json
import os
from PIL import Image, ImageColor, ImageTk

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
    "unknown": "#cc0000",
}

DEFAULT_UI = {
    "window_bg": "#2b2b2b",
    "panel_bg": "#3a3a3a",
    "button_bg": "#4a4a4a",
    "button_fg": "#ffffff",
    "grid_line": "#222222",
    "error_outline": "#ff3333",
    "selected_bg": "#2f6fb0",
}

# Вертикальное выравнивание неквадратных спрайтов внутри клетки:
# "top", "center" или "bottom". По горизонтали спрайт всегда по центру.
DEFAULT_ALIGN = {"box": "center", "goal": "center", "player": "center"}
ALIGN_VALUES = ("top", "center", "bottom")

# Клетки с объектами рисуются поверх пола. Для каждой клетки список вариантов:
# берётся первый, у которого есть все нужные текстуры. Слои кладутся по порядку.
OBJECT_LAYERS = {
    "box": [["box"]],
    "goal": [["goal"]],
    "player": [["player"]],
    "box_on_goal": [["box_on_goal"], ["goal", "box"]],
    "player_on_goal": [["player_on_goal"], ["goal", "player"]],
}

# какой ключ align относится к слою
ALIGN_KEY = {"box": "box", "box_on_goal": "box", "goal": "goal",
             "player": "player", "player_on_goal": "player"}


class Theme:
    """Тема оформления: текстуры клеток + цвета интерфейса.
    Тема это папка с PNG-файлами (wall.png, floor.png, ...) и необязательным theme.json.
    Коробка, цель и игрок рисуются поверх пола (текстуры или, если её нет, цвета пола),
    поэтому у них должен быть прозрачный фон.
    Если текстуры объекта нет, клетка рисуется цветным квадратом."""

    def __init__(self, folder=DEFAULT_THEME_DIR):
        self.folder = folder
        self.colors = dict(DEFAULT_COLORS)
        self.ui = dict(DEFAULT_UI)
        self.align = dict(DEFAULT_ALIGN)
        self._source = {}       # name -> PIL.Image (RGBA) или None
        self._cache = {}        # (name, size) -> ImageTk.PhotoImage или None
        self._floor_cache = {}  # size -> PIL.Image: пол нужного размера
        self._load_json()

    def _load_json(self):
        path = os.path.join(self.folder, "theme.json")
        if not os.path.isfile(path):
            return
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.colors.update(data.get("cells", {}))
        self.ui.update(data.get("ui", {}))
        for key, value in data.get("align", {}).items():
            if key in self.align and value in ALIGN_VALUES:
                self.align[key] = value

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

    def _floor_base(self, size):
        """Пол размером size×size: цвет пола, поверх него текстура (если есть)."""
        if size in self._floor_cache:
            return self._floor_cache[size]
        r, g, b = ImageColor.getrgb(self.colors["floor"])[:3]
        base = Image.new("RGBA", (size, size), (r, g, b, 255))
        floor = self._load_source("floor")
        if floor is not None:
            base = Image.alpha_composite(base, floor.resize((size, size), Image.NEAREST))
        self._floor_cache[size] = base
        return base

    def _fit(self, src, size, layer):
        """Вписывает спрайт в клетку size×size с сохранением пропорций.
        Свободное место остаётся прозрачным, и сквозь него виден пол."""
        w, h = src.size
        scale = size / max(w, h)
        new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
        sprite = src.resize((new_w, new_h), Image.NEAREST)
        align = self.align.get(ALIGN_KEY[layer], "center")
        x = (size - new_w) // 2
        y = {"top": 0, "bottom": size - new_h}.get(align, (size - new_h) // 2)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        canvas.paste(sprite, (x, y))
        return canvas

    def _render(self, name, size):
        """PIL-картинка клетки или None, если нужных текстур нет."""
        if name not in OBJECT_LAYERS:                  # стена, пол, неизвестная клетка
            src = self._load_source(name)
            return None if src is None else src.resize((size, size), Image.NEAREST)
        for layers in OBJECT_LAYERS[name]:
            sources = [self._load_source(layer) for layer in layers]
            if all(s is not None for s in sources):
                cell = self._floor_base(size)
                for layer, src in zip(layers, sources):
                    cell = Image.alpha_composite(cell, self._fit(src, size, layer))
                return cell
        return None

    def get_image(self, symbol, size):
        """PhotoImage нужного размера или None, если текстуры нет.
        Ссылки хранятся в кэше, иначе tkinter их «потеряет»."""
        name = SYMBOL_TO_NAME.get(symbol, "unknown")
        key = (name, size)
        if key in self._cache:
            return self._cache[key]
        img = self._render(name, size)
        photo = ImageTk.PhotoImage(img) if img is not None else None
        self._cache[key] = photo
        return photo

    def get_color(self, symbol):
        return self.colors[SYMBOL_TO_NAME.get(symbol, "unknown")]

    def clear_cache(self):
        """Вызывать при смене размера клетки, чтобы не копить старые картинки."""
        self._cache.clear()
        self._floor_cache.clear()