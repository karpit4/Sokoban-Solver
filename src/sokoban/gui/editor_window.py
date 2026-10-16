import os
import tkinter as tk
from tkinter import filedialog, messagebox

from gui.app import get_root
from gui.theme import Theme
from gui.board_view import BoardView
from gui.validation import validate
from gui.level_io import trim, save_txt

DEFAULT_SIZE = 16
MIN_SIZE = 3
MAX_SIZE = 40
UNDO_LIMIT = 100
PAD = 2            # пустое поле вокруг загруженного уровня
ICON_SIZE = 24

# gui -> sokoban -> src -> Sokoban (корень проекта)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LEVELS_DIR = os.path.join(PROJECT_DIR, "levels")

# (id, подпись, символ для значка, горячая клавиша)
TOOLS = [
    ("wall",   "Стена",   "#", "1"),
    ("floor",  "Пол",     "_", "2"),
    ("box",    "Коробка", "B", "3"),
    ("goal",   "Цель",    "X", "4"),
    ("player", "Игрок",   "P", "5"),
]

GOALS = {"X", "G", "Q"}
BOXES = {"B", "G"}
PLAYERS = {"P", "Q"}


def place(old, tool):
    """Новый символ клетки, если в клетку со значением old применили инструмент tool.
    Коробка и цель складываются в G, игрок и цель в Q. Коробка и игрок вместе не бывают."""
    if tool == "wall":
        return "#"
    if tool == "floor":
        return "_"
    goal, box, player = old in GOALS, old in BOXES, old in PLAYERS
    if tool == "goal":
        goal = True
    elif tool == "box":
        box, player = True, False
    elif tool == "player":
        player, box = True, False
    if player:
        return "Q" if goal else "P"
    if box:
        return "G" if goal else "B"
    return "X" if goal else "_"


def _cells_between(a, b):
    """Клетки на отрезке от a (не включая) до b (включая): при быстром движении
    мыши события приходят редко, и без этого в линии оставались бы дырки."""
    (i0, j0), (i1, j1) = a, b
    n = max(abs(i1 - i0), abs(j1 - j0))
    if n == 0:
        return [b]
    return [(int(i0 + (i1 - i0) * k / n + 0.5), int(j0 + (j1 - j0) * k / n + 0.5))
            for k in range(1, n + 1)]


class EditorWindow:
    
    def __init__(self, matrix, parent, theme):
        self.theme = theme
        self.result = None
        self._original = None    # задаётся ниже, после создания поля
        self._undo = []          # снимки матрицы до каждого действия
        self._before = None      # снимок на начало текущего мазка
        self._last_cell = None
        self._icons = {}         # ссылки на значки палитры

        ui = theme.ui
        self.win = tk.Toplevel(get_root() if parent is None else parent)
        if parent is not None:
            self.win.transient(parent)
        self.win.title("Конструктор уровня")
        self.win.configure(bg=ui["window_bg"], padx=12, pady=12)
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self._cancel)

        # палитра
        self.tool = tk.StringVar(value="wall")
        toolbar = tk.Frame(self.win, bg=ui["window_bg"])
        toolbar.pack(pady=(0, 8))
        for tool_id, text, symbol, key in TOOLS:
            tk.Radiobutton(
                toolbar, text=f" {key}  {text}", value=tool_id, variable=self.tool,
                image=self._icon(symbol), compound="left", indicatoron=False,
                bg=ui["button_bg"], fg=ui["button_fg"],
                selectcolor=ui.get("selected_bg", "#2f6fb0"),
                activebackground=ui["panel_bg"], activeforeground=ui["button_fg"],
                relief="flat", padx=8, pady=4,
            ).pack(side="left", padx=2)
            self.win.bind(f"<Key-{key}>", lambda e, t=tool_id: self.tool.set(t))

        # поле
        self.board = BoardView(self.win, theme)
        self.board.pack()
        self.board.set_matrix(self._initial_matrix(matrix))
        self._start = self.board.get_matrix()
        self._original = trim(self._start) if matrix else None

        # размер: для каждой стороны пара кнопок + и −
        size_row = tk.Frame(self.win, bg=ui["window_bg"])
        size_row.pack(pady=(8, 0))
        for side, title in (("top", "Сверху"), ("bottom", "Снизу"),
                            ("left", "Слева"), ("right", "Справа")):
            group = tk.Frame(size_row, bg=ui["window_bg"])
            group.pack(side="left", padx=8)
            tk.Label(group, text=title, bg=ui["window_bg"], fg=ui["button_fg"],
                     font=("Segoe UI", 9)).pack()
            pair = tk.Frame(group, bg=ui["window_bg"])
            pair.pack()
            self._button(pair, "+", lambda s=side: self._resize(s, 1), width=4).pack(side="left", padx=1)
            self._button(pair, "−", lambda s=side: self._resize(s, -1), width=4).pack(side="left", padx=1)

        self.size_label = tk.Label(self.win, bg=ui["window_bg"], fg=ui["button_fg"],
                                   font=("Segoe UI", 9))
        self.size_label.pack(pady=(6, 0))
        self.status_label = tk.Label(self.win, bg=ui["window_bg"], justify="left", anchor="w",
                                     wraplength=560, height=2, font=("Segoe UI", 10))
        self.status_label.pack(fill="x", pady=4)

        # нижние кнопки
        bottom = tk.Frame(self.win, bg=ui["window_bg"])
        bottom.pack(pady=(4, 0))
        self._button(bottom, "Отменить (Ctrl+Z)", self._undo_step, width=18).pack(side="left", padx=3)
        self._button(bottom, "Сохранить в .txt…", self._save, width=18).pack(side="left", padx=3)
        self._button(bottom, "Готово", self._done, width=12).pack(side="left", padx=3)
        self._button(bottom, "Отмена", self._cancel, width=12).pack(side="left", padx=3)

        # мышь: левая кнопка рисует выбранным инструментом, правая ставит пол
        c = self.board.canvas
        c.bind("<Button-1>", lambda e: self._press(e, None))
        c.bind("<B1-Motion>", lambda e: self._drag(e, None))
        c.bind("<ButtonRelease-1>", self._release)
        c.bind("<Button-3>", lambda e: self._press(e, "floor"))
        c.bind("<B3-Motion>", lambda e: self._drag(e, "floor"))
        c.bind("<ButtonRelease-3>", self._release)
        self.win.bind("<Control-KeyPress>", self._on_ctrl)

        self._refresh()
        self._bring_to_front()
    # ---------- оформление ----------

    def _button(self, parent, text, command, width):
        ui = self.theme.ui
        return tk.Button(parent, text=text, command=command, width=width,
                         bg=ui["button_bg"], fg=ui["button_fg"],
                         activebackground=ui["panel_bg"], activeforeground=ui["button_fg"],
                         relief="flat", pady=4)

    def _icon(self, symbol):
        """Значок палитры: текстура темы или, если её нет, цветной квадрат."""
        photo = self.theme.get_image(symbol, ICON_SIZE)
        if photo is None:
            photo = tk.PhotoImage(master=self.win, width=ICON_SIZE, height=ICON_SIZE)
            photo.put(self.theme.get_color(symbol), to=(0, 0, ICON_SIZE, ICON_SIZE))
        self._icons[symbol] = photo
        return photo

    def _bring_to_front(self):
        self.win.update_idletasks()
        w, h = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        x = (self.win.winfo_screenwidth() - w) // 2
        y = (self.win.winfo_screenheight() - h) // 3
        self.win.geometry(f"+{x}+{y}")
        self.win.attributes("-topmost", True)
        self.win.after(200, lambda: self.win.attributes("-topmost", False))
        self.win.focus_force()
        self.win.grab_set()

    # ---------- начальная матрица ----------

    @staticmethod
    def _initial_matrix(matrix):
        level = trim(matrix) if matrix else []
        if not level:
            return [["_"] * DEFAULT_SIZE for _ in range(DEFAULT_SIZE)]
        width = len(level[0]) + 2 * PAD
        pad_row = ["_"] * width
        return ([pad_row[:] for _ in range(PAD)]
                + [["_"] * PAD + row + ["_"] * PAD for row in level]
                + [pad_row[:] for _ in range(PAD)])

    # ---------- рисование ----------

    def _press(self, event, tool):
        self._before = self.board.get_matrix()
        self._last_cell = None
        self._paint(event, tool)

    def _drag(self, event, tool):
        self._paint(event, tool)

    def _paint(self, event, tool):
        tool = tool or self.tool.get()
        cell = self.board.cell_at(event.x, event.y)
        if cell is None or cell == self._last_cell:
            return
        cells = [cell] if self._last_cell is None else _cells_between(self._last_cell, cell)
        for i, j in cells:
            self._put(i, j, tool)
        self._last_cell = cell

    def _put(self, i, j, tool):
        if tool == "player":
            # игрок один: прежний убираем (на цели остаётся цель)
            for pi, row in enumerate(self.board.matrix):
                for pj, cell in enumerate(row):
                    if cell in PLAYERS and (pi, pj) != (i, j):
                        self.board.set_cell(pi, pj, "X" if cell == "Q" else "_")
        self.board.set_cell(i, j, place(self.board.matrix[i][j], tool))

    def _release(self, event):
        """Конец мазка: если что-то изменилось, он становится одним шагом отмены."""
        if self._before is not None and self._before != self.board.matrix:
            self._push_undo(self._before)
            self._refresh()
        self._before = None
        self._last_cell = None

    # ---------- отмена ----------

    def _push_undo(self, snapshot):
        self._undo.append(snapshot)
        if len(self._undo) > UNDO_LIMIT:
            self._undo.pop(0)

    def _undo_step(self):
        if not self._undo:
            return
        self.board.set_matrix(self._undo.pop())
        self._refresh()

    def _on_ctrl(self, event):
        # keycode 90 это клавиша Z в Windows при любой раскладке
        if event.keycode == 90 or event.keysym.lower() == "z":
            self._undo_step()

    # ---------- размер ----------

    def _resize(self, side, delta):
        """side: "top", "bottom", "left" или "right"; delta: +1 добавить, -1 убрать."""
        m = self.board.get_matrix()
        rows, cols = len(m), len(m[0])
        size = rows if side in ("top", "bottom") else cols
        if (delta > 0 and size >= MAX_SIZE) or (delta < 0 and size <= MIN_SIZE):
            return
        self._push_undo(self.board.get_matrix())

        if side == "top":
            m.insert(0, ["_"] * cols) if delta > 0 else m.pop(0)
        elif side == "bottom":
            m.append(["_"] * cols) if delta > 0 else m.pop()
        elif side == "left":
            for row in m:
                row.insert(0, "_") if delta > 0 else row.pop(0)
        else:  # right
            for row in m:
                row.append("_") if delta > 0 else row.pop()

        self.board.set_matrix(m)
        self._refresh()

    # ---------- статус ----------

    def _refresh(self):
        trimmed = trim(self.board.matrix)
        final = f"{len(trimmed)}×{len(trimmed[0])}" if trimmed else "пусто"
        self.size_label.config(
            text=f"Размер сетки: {self.board.rows}×{self.board.cols}   "
                 f"Размер уровня: {final}")

        ui = self.theme.ui
        issues = validate(self.board.matrix)
        if issues:
            self.status_label.config(text="  •  ".join(i.message for i in issues),
                                     fg=ui["error_outline"])
        else:
            self.status_label.config(text="Ошибок не найдено", fg=ui["button_fg"])

    # ---------- сохранение и выход ----------

    def _save(self):
        initial = LEVELS_DIR if os.path.isdir(LEVELS_DIR) else PROJECT_DIR
        path = filedialog.asksaveasfilename(
            parent=self.win, title="Сохранить уровень", initialdir=initial,
            defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt")])
        if not path:
            return
        try:
            save_txt(path, self.board.matrix)
        except (ValueError, OSError) as e:
            messagebox.showerror("Не удалось сохранить", str(e), parent=self.win)
            return
        messagebox.showinfo("Сохранено", path, parent=self.win)

    def _done(self):
        level = trim(self.board.matrix)
        if not level:
            messagebox.showwarning("Пустое поле", "Нарисуйте уровень или нажмите «Отмена».",
                                   parent=self.win)
            return
        # None означает «без изменений» (так и ждёт confirm_window)
        self.result = None if level == self._original else level
        self.win.destroy()

    def _cancel(self):
        if self.board.matrix != self._start and not messagebox.askyesno(
                "Закрыть конструктор", "Изменения не будут сохранены. Закрыть?", parent=self.win):
            return
        self.result = None
        self.win.destroy()


def edit_level(matrix=None, parent=None, theme=None):
    """Открывает редактор. matrix=None: новый уровень с нуля (сетка 16×16).
    Возвращает матрицу без пустых краёв или None (отмена или нет изменений).
    Подходит как edit_callback для confirm_levels."""
    get_root()                 # корень должен существовать до создания Theme
    theme = theme or Theme()
    window = EditorWindow(matrix, parent, theme)
    window.win.wait_window()
    return window.result