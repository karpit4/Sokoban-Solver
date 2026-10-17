import tkinter as tk
from tkinter import messagebox

from core.rules import DIRECTIONS
from core.session import GameSession
from core.state import symbol_at
from gui.app import bring_to_front, get_root
from gui.board_view import BoardView
from gui.styling import Styler
from gui.theme import ThemeManager

# Стрелки приходят как keysym ("Up", "Down", "Left", "Right": те же имена, что в DIRECTIONS).
# Буквы определяются по коду клавиши, чтобы работали в любой раскладке (коды Windows).
WASD_KEYCODES = {87: "Up", 65: "Left", 83: "Down", 68: "Right"}   # W, A, S, D
UNDO_KEYCODE = 90      # Z
RESTART_KEYCODE = 82   # R


class GameFrame(tk.Frame):
    """Окно игры в виде Frame: его можно поместить и в отдельное окно (play_level),
    и позже в главное окно программы.
    on_exit(won, moves) вызывается, когда игрок нажал «Выйти»:
    won - пройден ли уровень, moves - сделанные ходы."""

    def __init__(self, master, matrix, name, themes, on_exit):
        super().__init__(master, padx=12, pady=12)
        self.themes = themes
        self.theme = themes.theme
        self.on_exit = on_exit
        self.session = GameSession(matrix)
        self.styler = Styler()
        self.styler.add(self, "bg")

        self._label(self, text=name, font=("Segoe UI", 12, "bold")).pack(pady=(0, 8))

        self.board = BoardView(self, self.theme)
        self.board.pack()
        self.board.set_matrix(matrix)

        self.status_label = self._label(self, font=("Segoe UI", 11, "bold"))
        self.status_label.pack(pady=(8, 0))
        self._label(self, text="Стрелки/WASD: ход    Клик: перейти    Z: отмена    R: заново",
                    font=("Segoe UI", 9)).pack(pady=(2, 8))

        buttons = self._frame(self)
        buttons.pack()
        self.undo_btn = self._button(buttons, "Отменить (Z)", self._undo)
        self.restart_btn = self._button(buttons, "Заново (R)", self._restart)
        self.exit_btn = self._button(buttons, "Выйти", self.close)
        for btn in (self.undo_btn, self.restart_btn, self.exit_btn):
            btn.pack(side="left", padx=4)

        # смена темы: ◀ название ▶
        theme_row = self._frame(self)
        theme_row.pack(pady=(8, 0))
        self.prev_theme_btn = self._button(theme_row, "◀", lambda: self._change_theme(-1), width=3)
        self.theme_label = self._label(theme_row, width=18)
        self.next_theme_btn = self._button(theme_row, "▶", lambda: self._change_theme(1), width=3)
        self.prev_theme_btn.pack(side="left")
        self.theme_label.pack(side="left", padx=4)
        self.next_theme_btn.pack(side="left")
        if len(self.themes.names()) < 2:
            self.prev_theme_btn.config(state="disabled")
            self.next_theme_btn.config(state="disabled")

        self.styler.apply(self.theme)
        self._update_theme_label()
        self.themes.subscribe(self, self._on_theme_change)

        # Клавиши ловит сам Frame, поэтому после каждого нажатия кнопки фокус возвращается ему
        self.bind("<Key>", self._on_key)
        self.board.canvas.bind("<Button-1>", self._on_click)
        self._update_status()

    # ---------- оформление ----------

    def _frame(self, parent):
        return self.styler.add(tk.Frame(parent), "bg")

    def _label(self, parent, **options):
        return self.styler.add(tk.Label(parent, **options), "label")

    def _button(self, parent, text, command, width=14):
        def run():
            command()
            if self.winfo_exists():      # «Выйти» уже закрыло окно
                self.focus_set()
        btn = tk.Button(parent, text=text, command=run, width=width, relief="flat", pady=4)
        return self.styler.add(btn, "button")

    def _update_theme_label(self):
        self.theme_label.config(text=f"Тема: {self.themes.name}")

    def _change_theme(self, step):
        self.themes.cycle(step)      # менеджер сам вызовет _on_theme_change

    def _on_theme_change(self, theme):
        self.theme = theme
        self.styler.apply(theme)
        self._update_theme_label()
        self.board.set_theme(theme)  # перерисовывает текущее положение, а не начальное
        self._update_status()

    # ---------- игра ----------

    def _apply(self, cells):
        """Перерисовывает только изменившиеся клетки и обновляет строку состояния."""
        state = self.session.state
        for i, j in cells:
            self.board.set_cell(i, j, symbol_at(state, (i, j)))
        self._update_status()

    def _update_status(self):
        n = self.session.move_count
        if self.session.is_won:
            self.status_label.config(text=f"Уровень пройден! Ходов: {n}")
        else:
            self.status_label.config(text=f"Ходов: {n}")
        state = "normal" if self.session.can_undo else "disabled"
        self.undo_btn.config(state=state)
        self.restart_btn.config(state=state)

    def _on_key(self, event):
        direction = event.keysym if event.keysym in DIRECTIONS else WASD_KEYCODES.get(event.keycode)
        if direction:
            self._apply(self.session.move(direction))
        elif event.keycode == UNDO_KEYCODE:
            self._undo()
        elif event.keycode == RESTART_KEYCODE:
            self._restart()

    def _on_click(self, event):
        """Клик по клетке: игрок идёт туда, если дойти можно, не двигая коробки."""
        self.focus_set()
        cell = self.board.cell_at(event.x, event.y)
        if cell is not None:
            self._apply(self.session.walk_to(cell))

    def _undo(self):
        self._apply(self.session.undo())

    def _restart(self):
        if self.session.can_undo and not self.session.is_won:
            if not messagebox.askyesno("Заново", "Начать уровень сначала? Ходы будут потеряны.",
                                       parent=self):
                self.focus_set()
                return
        self._apply(self.session.restart())

    def close(self):
        self.on_exit(self.session.is_won, self.session.moves)


def play_level(matrix, name="", parent=None, themes=None):
    """Открывает окно игры и ждёт, пока игрок его закроет.
    Возвращает (won, moves): пройден ли уровень и список сделанных ходов."""
    get_root()                     # корень должен существовать до создания окна
    if themes is None:
        themes = ThemeManager()

    win = tk.Toplevel(get_root() if parent is None else parent)
    if parent is not None:
        win.transient(parent)
    win.title("Игра")
    win.resizable(False, False)

    result = {"won": False, "moves": []}

    def finish(won, moves):
        result["won"], result["moves"] = won, moves
        win.destroy()

    frame = GameFrame(win, matrix, name, themes, finish)
    frame.pack()
    win.protocol("WM_DELETE_WINDOW", frame.close)
    bring_to_front(win)
    frame.focus_set()              # после focus_force окна: клавиши идут во Frame
    win.wait_window()
    get_root().update()            # окно должно исчезнуть до следующих действий
    return result["won"], result["moves"]