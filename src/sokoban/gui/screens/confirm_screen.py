import tkinter as tk

from gui.board_view import BoardView
from gui.screens.editor_screen import EditorScreen
from gui.screens.base import Screen
from gui.settings import open_settings
from levels.validation import validate


class ConfirmScreen(Screen):
    """Подтверждение уровней: показывает их по одному, кнопки Подтвердить / Изменить / Пропустить.
    on_done(levels) вызывается после последнего уровня со списком подтверждённых (может быть пустым),
    on_cancel() по кнопке «Отмена»: тогда ни один уровень дальше не идёт."""

    def __init__(self, master, app, levels, on_done, on_cancel, index=0, result=None):
        super().__init__(master, app)
        self.levels = [(name, [list(row) for row in matrix]) for name, matrix in levels]
        self.on_done = on_done
        self.on_cancel = on_cancel
        self.index = index
        self.result = result if result is not None else []
        self.configure(padx=24, pady=20)

        self.title_label = self.label(self, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(pady=(0, 8))

        self.board = BoardView(self, app.themes.theme)
        self.board.pack()

        # цвет текста задаёт _refresh_issues, поэтому роль только «фон»
        self.issues_label = self.styler.add(
            tk.Label(self, justify="left", anchor="w", font=("Segoe UI", 10)), "bg")
        self.issues_label.pack(fill="x", pady=8)

        buttons = self.frame(self)
        buttons.pack()
        self.confirm_btn = self.button(buttons, "Подтвердить", self._confirm, width=13)
        self.edit_btn = self.button(buttons, "Изменить", self._edit, width=13)
        self.skip_btn = self.button(buttons, "Пропустить", self._skip, width=13)
        self.settings_btn = self.button(buttons, "Настройки", self._open_settings, width=13)
        self.cancel_btn = self.button(buttons, "Отмена", self._cancel, width=13)
        for btn in (self.confirm_btn, self.edit_btn, self.skip_btn,
                    self.settings_btn, self.cancel_btn):
            btn.pack(side="left", padx=4)

        self.bind("<Return>", lambda e: self._confirm())
        self._show_level()

    def on_theme_change(self, theme):
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

        ui = self.app.themes.theme.ui
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
            self.on_done(self.result)
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
        """Открывает конструктор с этим уровнем и возвращается на то же место
        с исправленным уровнем («Готово») или без изменений («Отмена»)."""
        name, matrix = self.levels[self.index]
        levels, index, result = self.levels, self.index, self.result
        on_done, on_cancel = self.on_done, self.on_cancel

        def resume(new_matrix=None):
            if new_matrix is not None:
                levels[index] = (name, new_matrix)
            self.app.show(ConfirmScreen, levels, on_done, on_cancel, index, result)

        self.app.show(EditorScreen, matrix, on_done=resume, on_cancel=resume)
        
    def _open_settings(self):
        open_settings(self.app.themes, self.app.root)
        self.focus_set()

    def _cancel(self):
        self.on_cancel()