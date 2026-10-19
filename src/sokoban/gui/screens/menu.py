from gui.screens.base import Screen
from gui.screens.play_menu import PlayMenuScreen
from gui.screens.solve_menu import SolveMenuScreen


class MenuScreen(Screen):
    """Главное меню."""

    def __init__(self, master, app):
        super().__init__(master, app)
        self.configure(padx=60, pady=40)
        self.label(self, text="Sokoban", font=("Segoe UI", 28, "bold")).pack(pady=(0, 30))
        self._big_button("Играть", self._play).pack(pady=6)
        self._big_button("Решить уровень", self._solve).pack(pady=6)
        self._big_button("Настройки", self._settings).pack(pady=6)

    def _big_button(self, text, command):
        return self.button(self, text, command, width=24, font=("Segoe UI", 13), pady=10)

    def _back(self):
        self.app.show(MenuScreen)

    def _play(self):
        self.app.show(PlayMenuScreen, self._back)

    def _solve(self):
        self.app.show(SolveMenuScreen, self._back)

    def _settings(self):
        self.app.open_settings()