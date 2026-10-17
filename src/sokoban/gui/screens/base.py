import tkinter as tk

from gui.styling import Styler


class Screen(tk.Frame):
    """Базовый класс экрана главного окна.
    Экран создаётся, когда его показывают (App.show), и уничтожается, когда показывают другой,
    поэтому состояние экрана не переживает переход. Что нужно помнить между экранами,
    передаётся аргументами или хранится в App.
    Цвета ставятся сами: виджеты, созданные через frame/label/button, регистрируются
    в Styler, а App.show и смена темы вызывают перекраску."""

    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.styler = Styler()
        self.styler.add(self, "bg")
        app.themes.subscribe(self, self._on_theme_change)

    def frame(self, parent, **options):
        return self.styler.add(tk.Frame(parent, **options), "bg")

    def label(self, parent, **options):
        return self.styler.add(tk.Label(parent, **options), "label")

    def button(self, parent, text, command, width=14, **options):
        settings = dict(relief="flat", pady=4)
        settings.update(options)
        btn = tk.Button(parent, text=text, command=command, width=width, **settings)
        return self.styler.add(btn, "button")

    def _on_theme_change(self, theme):
        self.styler.apply(theme)
        self.on_theme_change(theme)

    def on_theme_change(self, theme):
        """Переопределите, если экран держит то, что Styler не перекрашивает
        (игровое поле, значки)."""