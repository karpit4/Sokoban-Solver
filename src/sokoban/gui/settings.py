import tkinter as tk

from gui.styling import Styler


class SettingsFrame(tk.Frame):
    """Содержимое настроек. Сейчас здесь только смена темы; новые настройки добавляются сюда
    и сразу появляются на экране настроек."""

    def __init__(self, master, themes):
        super().__init__(master, padx=24, pady=20)
        self.themes = themes
        self.styler = Styler()
        self.styler.add(self, "bg")

        self._label(self, text="Тема оформления", font=("Segoe UI", 12, "bold")).pack(pady=(0, 8))
        row = self._frame(self)
        row.pack()
        self.prev_btn = self._button(row, "◀", lambda: self.themes.cycle(-1), width=3)
        self.theme_label = self._label(row, width=18)
        self.next_btn = self._button(row, "▶", lambda: self.themes.cycle(1), width=3)
        self.prev_btn.pack(side="left")
        self.theme_label.pack(side="left", padx=4)
        self.next_btn.pack(side="left")
        if len(self.themes.names()) < 2:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")

        self.styler.apply(self.themes.theme)
        self._update_label()
        self.themes.subscribe(self, self._on_theme_change)

    def _frame(self, parent):
        return self.styler.add(tk.Frame(parent), "bg")

    def _label(self, parent, **options):
        return self.styler.add(tk.Label(parent, **options), "label")

    def _button(self, parent, text, command, width):
        btn = tk.Button(parent, text=text, command=command, width=width, relief="flat", pady=4)
        return self.styler.add(btn, "button")

    def _update_label(self):
        self.theme_label.config(text=f"Тема: {self.themes.name}")

    def _on_theme_change(self, theme):
        self.styler.apply(theme)
        self._update_label()