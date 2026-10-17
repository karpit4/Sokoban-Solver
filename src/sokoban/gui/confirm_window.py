import tkinter as tk

from gui.app import get_root
from gui.board_view import BoardView
from gui.styling import Styler
from gui.theme import ThemeManager
from levels.validation import validate


class ConfirmWindow:
    """Показывает уровни по одному: Подтвердить / Изменить / Пропустить.
    Кнопка темы переключает оформление по кругу."""

    def __init__(self, levels, themes, edit_callback):
        self.levels = [(name, [list(row) for row in matrix]) for name, matrix in levels]
        self.themes = themes
        self.theme = themes.theme
        self.edit_callback = edit_callback
        self.index = 0
        self.result = []
        self.styler = Styler()

        self.win = tk.Toplevel(get_root())
        self.win.title("Подтверждение уровня")
        self.win.configure(padx=12, pady=12)
        self.styler.add(self.win, "bg")
        self.win.protocol("WM_DELETE_WINDOW", self._cancel)

        self.title_label = self.styler.add(
            tk.Label(self.win, font=("Segoe UI", 12, "bold")), "label")
        self.title_label.pack(pady=(0, 8))

        self.board = BoardView(self.win, self.theme)
        self.board.pack()

        self.issues_label = self.styler.add(
            tk.Label(self.win, justify="left", anchor="w", font=("Segoe UI", 10)), "bg")
        self.issues_label.pack(fill="x", pady=8)

        self.buttons_frame = self.styler.add(tk.Frame(self.win), "bg")
        self.buttons_frame.pack()
        
        self.confirm_btn = self._button("Подтвердить", self._confirm)
        self.edit_btn = self._button("Изменить", self._edit)
        self.skip_btn = self._button("Пропустить", self._skip)
        for btn in (self.confirm_btn, self.edit_btn, self.skip_btn):
            btn.pack(side="left", padx=4)
        if self.edit_callback is None:
            self.edit_btn.config(state="disabled")

        # смена темы: ◀ название ▶
        theme_box = self.styler.add(tk.Frame(self.buttons_frame), "bg")
        theme_box.pack(side="left", padx=(12, 4))
        self.prev_theme_btn = self._button("◀", lambda: self._change_theme(-1),
                                           width=3, parent=theme_box)
        self.theme_label = self.styler.add(tk.Label(theme_box, width=18), "label")
        self.next_theme_btn = self._button("▶", lambda: self._change_theme(1),
                                           width=3, parent=theme_box)
        self.prev_theme_btn.pack(side="left")
        self.theme_label.pack(side="left", padx=4)
        self.next_theme_btn.pack(side="left")
        if len(self.themes.names()) < 2:
            self.prev_theme_btn.config(state="disabled")
            self.next_theme_btn.config(state="disabled")

        self.styler.apply(self.theme)
        self._update_theme_button()
        self.themes.subscribe(self.win, self._on_theme_change)

        self.win.bind("<Return>", lambda e: self._confirm())
        self._show_level()
        self._bring_to_front()


    def _button(self, text, command, width=14, parent=None):
        btn = tk.Button(parent or self.buttons_frame, text=text, command=command,
                        width=width, relief="flat", pady=4)
        return self.styler.add(btn, "button")

    def _update_theme_button(self):
        self.theme_label.config(text=f"Тема: {self.themes.name}")

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

    # ---------- смена темы ----------

    def _change_theme(self, step):
        self.themes.cycle(step)      # менеджер сам вызовет _on_theme_change

    def _on_theme_change(self, theme):
        """Вызывается менеджером, в том числе когда тему сменили в редакторе."""
        self.theme = theme
        self.styler.apply(theme)
        self._update_theme_button()
        self.board.set_theme(theme)
        self._refresh_issues()

    # ---------- показ уровня ----------

    def _show_level(self):
        name, matrix = self.levels[self.index]
        self.title_label.config(text=f"Уровень {self.index + 1} из {len(self.levels)}: {name}")
        self.board.set_matrix(matrix)
        self._refresh_issues()

    def _refresh_issues(self):
        """Проверяет текущий уровень, рисует подсветку и обновляет кнопку подтверждения."""
        _, matrix = self.levels[self.index]
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


def confirm_levels(levels_info, themes=None, edit_callback=None):
    """levels_info: список (имя, матрица), как возвращает choose_parsing().
    themes: ThemeManager (если не передать, создаётся новый).
    edit_callback(matrix, parent) -> новая матрица или None (если изменений нет).
    Возвращает список подтверждённых (имя, матрица). Пропущенные уровни не включаются."""
    if not levels_info:
        return []
    get_root()                       # корень должен существовать до создания окон
    if themes is None:
        themes = ThemeManager()
    window = ConfirmWindow(levels_info, themes, edit_callback)
    window.win.wait_window()         # блокируем, пока окно не закроется
    get_root().update()              # окно должно исчезнуть до запуска pyautogui
    return window.result