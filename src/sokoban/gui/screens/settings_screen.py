from gui.screens.base import Screen
from gui.settings import SettingsFrame


class SettingsScreen(Screen):
    """Экран настроек в главном окне. back() вызывается по кнопке «Назад» и по Escape.
    Содержимое по центру: окно на время настроек сохраняет размер предыдущего экрана."""

    def __init__(self, master, app, back):
        super().__init__(master, app)
        self.configure(padx=60, pady=40)
        inner = self.frame(self)
        inner.pack(expand=True)
        self.label(inner, text="Настройки", font=("Segoe UI", 20, "bold")).pack(pady=(0, 16))
        SettingsFrame(inner, app.themes).pack()
        self.button(inner, "Назад", back, width=16).pack(pady=(18, 0))
        self.bind("<Escape>", lambda e: back())