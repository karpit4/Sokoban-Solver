import os
from tkinter import filedialog, messagebox

from gui.screens.editor_screen import EditorScreen
from gui.screens.base import Screen
from gui.screens.confirm_screen import ConfirmScreen
from gui.screens.solve_screen import SolveScreen
from levels.loaders import parse_txt
from paths import PROJECT_DIR


def load_txt_levels(paths):
    """Читает уровни из .txt файлов. Возвращает (уровни, ошибки): уровни это список
    (название, матрица). Название это имя файла, а для файла с несколькими уровнями
    ещё и номер: «pack #2». Файл, который не удалось прочитать, даёт строку в ошибках."""
    levels, errors = [], []
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            parsed = parse_txt(path)
        except (ValueError, OSError) as e:
            errors.append(str(e))
            continue
        for i, level in enumerate(parsed, start=1):
            levels.append((name if len(parsed) == 1 else f"{name} #{i}", level))
    return levels, errors


class SolveMenuScreen(Screen):
    """Меню «Решить уровень»: уровни из .txt файлов или нарисованные в конструкторе.
    back() вызывается по кнопке «Назад»."""

    def __init__(self, master, app, back):
        super().__init__(master, app)
        self._back = back
        self.configure(padx=60, pady=40)
        self.label(self, text="Решить уровень", font=("Segoe UI", 20, "bold")).pack(pady=(0, 24))
        self._big_button("Из файла (.txt)", self._from_file).pack(pady=6)
        self._big_button("Нарисовать в конструкторе", self._from_editor).pack(pady=6)
        self.button(self, "Назад", back, width=16).pack(pady=(18, 0))

    def _big_button(self, text, command):
        return self.button(self, text, command, width=28, font=("Segoe UI", 13), pady=10)

    def _return_here(self):
        """Куда вернуться, когда работа закончена или отменена."""
        self.app.show(SolveMenuScreen, self._back)

    # ---------- из файла ----------

    def _from_file(self):
        root = self.app.root
        paths = filedialog.askopenfilenames(
            parent=root, title="Выберите файлы с уровнями", initialdir=PROJECT_DIR,
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        if isinstance(paths, str):               # на некоторых версиях Tk приходит строка
            paths = root.tk.splitlist(paths)
        if not paths:
            return
        levels, errors = load_txt_levels(paths)
        if errors:
            messagebox.showerror("Не удалось прочитать файлы", "\n".join(errors), parent=root)
        if levels:
            self.app.show(ConfirmScreen, levels,
                          on_done=self._confirmed, on_cancel=self._return_here)

    def _confirmed(self, levels):
        if not levels:
            messagebox.showinfo("Нет подтверждённых уровней",
                                "Ни один уровень не подтверждён, решать нечего.",
                                parent=self.app.root)
            self._return_here()
            return
        self.app.show(SolveScreen, levels, self._return_here)

    # ---------- из конструктора ----------

    def _from_editor(self):
        """Конструктор не даёт закончить некорректный уровень, поэтому подтверждение не нужно."""
        self.app.show(EditorScreen, None, on_done=self._solve_own, on_cancel=self._return_here)

    def _solve_own(self, level):
        self.app.show(SolveScreen, [("свой уровень", level)], self._return_here)