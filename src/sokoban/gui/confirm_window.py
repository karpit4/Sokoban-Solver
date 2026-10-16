import tkinter as tk

from gui.app import get_root
from gui.theme import Theme
from gui.board_view import BoardView
from gui.validation import validate


class ConfirmWindow:
    """Показывает уровни по одному: Подтвердить / Изменить / Пропустить."""

    def __init__(self, levels, theme, edit_callback):
        self.levels = [(name, [list(row) for row in matrix]) for name, matrix in levels]
        self.theme = theme
        self.edit_callback = edit_callback
        self.index = 0
        self.result = []

        ui = theme.ui
        self.win = tk.Toplevel(get_root())
        self.win.title("Подтверждение уровня")
        self.win.configure(bg=ui["window_bg"], padx=12, pady=12)
        self.win.protocol("WM_DELETE_WINDOW", self._cancel)

        self.title_label = tk.Label(self.win, bg=ui["window_bg"], fg=ui["button_fg"],
                                    font=("Segoe UI", 12, "bold"))
        self.title_label.pack(pady=(0, 8))

        self.board = BoardView(self.win, theme)
        self.board.pack()

        self.issues_label = tk.Label(self.win, bg=ui["window_bg"], justify="left",
                                     anchor="w", font=("Segoe UI", 10))
        self.issues_label.pack(fill="x", pady=8)

        buttons = tk.Frame(self.win, bg=ui["window_bg"])
        buttons.pack()
        self.confirm_btn = self._button(buttons, "Подтвердить", self._confirm)
        self.edit_btn = self._button(buttons, "Изменить", self._edit)
        self.skip_btn = self._button(buttons, "Пропустить", self._skip)
        for btn in (self.confirm_btn, self.edit_btn, self.skip_btn):
            btn.pack(side="left", padx=4)
        if self.edit_callback is None:
            self.edit_btn.config(state="disabled")

        self.win.bind("<Return>", lambda e: self._confirm())
        self._show_level()
        self._bring_to_front()

    def _button(self, parent, text, command):
        ui = self.theme.ui
        return tk.Button(parent, text=text, command=command, width=14,
                         bg=ui["button_bg"], fg=ui["button_fg"],
                         activebackground=ui["panel_bg"], activeforeground=ui["button_fg"],
                         relief="flat", pady=4)

    def _bring_to_front(self):
        """Окно создаётся из консольной программы и иначе может оказаться под другими окнами."""
        self.win.update_idletasks()
        w, h = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        x = (self.win.winfo_screenwidth() - w) // 2
        y = (self.win.winfo_screenheight() - h) // 3
        self.win.geometry(f"+{x}+{y}")
        self.win.attributes("-topmost", True)
        self.win.after(200, lambda: self.win.attributes("-topmost", False))
        self.win.focus_force()
        self.win.grab_set()

    # ---------- показ уровня ----------

    def _show_level(self):
        name, matrix = self.levels[self.index]
        self.title_label.config(text=f"Уровень {self.index + 1} из {len(self.levels)}: {name}")
        self.board.set_matrix(matrix)

        issues = validate(matrix)
        cells = [cell for issue in issues for cell in issue.cells]
        self.board.highlight(cells)

        ui = self.theme.ui
        if issues:
            text = "\n".join("• " + issue.message for issue in issues)
            self.issues_label.config(text=text, fg=ui["error_outline"])
            self.confirm_btn.config(state="disabled")
        else:
            self.issues_label.config(text="Ошибок не найдено", fg=ui["button_fg"])
            self.confirm_btn.config(state="normal")

    def _next(self):
        self.index += 1
        if self.index >= len(self.levels):
            self.win.destroy()
        else:
            self._show_level()

    # ---------- кнопки ----------

    def _confirm(self):
        if str(self.confirm_btn["state"]) == "disabled":   # Enter тоже сюда приходит
            return
        name, matrix = self.levels[self.index]
        self.result.append((name, matrix))
        self._next()

    def _skip(self):
        self._next()

    def _edit(self):
        name, matrix = self.levels[self.index]
        new_matrix = self.edit_callback(matrix, self.win)
        if new_matrix is not None:
            self.levels[self.index] = (name, new_matrix)
        self._show_level()
        self.win.grab_set()   # после вложенного окна возвращаем фокус себе

    def _cancel(self):
        """Закрытие крестиком: оставшиеся уровни не попадают в результат."""
        self.win.destroy()


def confirm_levels(levels_info, theme=None, edit_callback=None):
    """levels_info: список (имя, матрица), как возвращает choose_parsing().
    edit_callback(matrix, parent) -> новая матрица или None (если изменений нет).
    Возвращает список подтверждённых (имя, матрица). Пропущенные уровни не включаются."""
    if not levels_info:
        return []
    get_root()                       # корень должен существовать до создания Theme
    theme = theme or Theme()
    window = ConfirmWindow(levels_info, theme, edit_callback)
    window.win.wait_window()         # блокируем, пока окно не закроется
    get_root().update()              # окно должно исчезнуть до запуска pyautogui
    return window.result