import tkinter as tk

from gui.screens.base import Screen
from gui.screens.game import play_library_level
from levels import library
from paths import LIBRARY_DIR


class PickLevelScreen(Screen):
    """Выбор уровня из библиотеки: поиск по части названия и список.
    Enter или двойной клик открывают выбранный уровень, стрелки вверх и вниз
    двигают выбор прямо из строки поиска. back() вызывается по кнопке «Назад»."""

    def __init__(self, master, app, back):
        super().__init__(master, app)
        self._back = back
        self._matches = []
        self.entry = None
        self.configure(padx=40, pady=30)
        self.label(self, text="Выбор уровня", font=("Segoe UI", 20, "bold")).pack(pady=(0, 12))

        self._total = len(library.list_names())
        if self._total == 0:
            self.label(self, text=f"В библиотеке нет уровней:\n{LIBRARY_DIR}",
                       font=("Segoe UI", 11), justify="center").pack(pady=(0, 16))
            self.button(self, "Назад", back, width=16).pack()
            return

        self.query = tk.StringVar()
        self.entry = self.styler.add(
            tk.Entry(self, textvariable=self.query, width=36, relief="flat",
                     font=("Segoe UI", 12)), "entry")
        self.entry.pack(fill="x", pady=(0, 8), ipady=4)

        list_frame = self.frame(self)
        list_frame.pack(fill="both", expand=True)
        self.listbox = self.styler.add(
            tk.Listbox(list_frame, height=12, exportselection=False, activestyle="none",
                       relief="flat", font=("Segoe UI", 11)), "list")
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)

        self.count_label = self.label(self, font=("Segoe UI", 9))
        self.count_label.pack(pady=(6, 8))

        buttons = self.frame(self)
        buttons.pack()
        self.button(buttons, "Играть", self._play, width=14).pack(side="left", padx=4)
        self.button(buttons, "Назад", back, width=14).pack(side="left", padx=4)

        self.query.trace_add("write", lambda *_: self._refresh())
        self.entry.bind("<Return>", lambda e: self._play())
        self.entry.bind("<Down>", lambda e: self._move(1))
        self.entry.bind("<Up>", lambda e: self._move(-1))
        self.listbox.bind("<Double-Button-1>", lambda e: self._play())
        self.listbox.bind("<Return>", lambda e: self._play())
        self._refresh()

    def focus_set(self):
        if self.entry is not None:
            self.entry.focus_set()
        else:
            super().focus_set()

    def _refresh(self):
        """Перестраивает список по тексту запроса и выбирает первый уровень."""
        self._matches = library.find(self.query.get())
        self.listbox.delete(0, "end")
        for name in self._matches:
            self.listbox.insert("end", name)
        if self._matches:
            self._select(0)
        self.count_label.config(text=f"Найдено: {len(self._matches)} из {self._total}")

    def _select(self, index):
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def _move(self, step):
        if self._matches:
            current = self.listbox.curselection()
            index = (current[0] if current else -1) + step
            self._select(min(max(index, 0), len(self._matches) - 1))
        return "break"                 # курсор в строке поиска не двигается

    def _play(self):
        current = self.listbox.curselection()
        if not current:
            return
        back = self._back
        play_library_level(self.app, self._matches[current[0]],
                           back=lambda: self.app.show(PickLevelScreen, back))