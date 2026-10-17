from gui.screens.base import Screen
from gui.settings import SettingsFrame


class SettingsScreen(Screen):
    """Экран настроек в главном окне. back() вызывается по кнопке «Назад»."""

    def __init__(self, master, app, back):
        super().__init__(master, app)
        self.configure(padx=60, pady=40)
        self.label(self, text="Настройки", font=("Segoe UI", 20, "bold")).pack(pady=(0, 16))
        SettingsFrame(self, app.themes).pack()
        self.button(self, "Назад", back, width=16).pack(pady=(18, 0))