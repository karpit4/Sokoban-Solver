from tkinter import messagebox
from gui.editor_window import edit_level
from gui.screens.base import Screen
from gui.screens.game import GameScreen, play_library_level
from gui.screens.pick_level import PickLevelScreen
from levels import library
from paths import LIBRARY_DIR


class PlayMenuScreen(Screen):
    """Меню «Играть»: свой уровень, случайный, выбрать из библиотеки.
    back() вызывается по кнопке «Назад»."""

    def __init__(self, master, app, back):
        super().__init__(master, app)
        self._back = back
        self.configure(padx=60, pady=40)
        self.label(self, text="Играть", font=("Segoe UI", 20, "bold")).pack(pady=(0, 24))
        self._big_button("Свой уровень", self._own_level).pack(pady=6)
        self._big_button("Случайный уровень", self._random_level).pack(pady=6)
        self._big_button("Выбрать уровень", self._pick_level).pack(pady=6)
        self.button(self, "Назад", back, width=16).pack(pady=(18, 0))

    def _big_button(self, text, command):
        return self.button(self, text, command, width=24, font=("Segoe UI", 13), pady=10)

    def _return_here(self):
        """Куда вернуться после игры."""
        self.app.show(PlayMenuScreen, self._back)

    def _own_level(self):
        """Конструктор, затем игра. Конструктор не даёт закончить некорректный уровень,
        поэтому отдельное подтверждение не нужно. Пока конструктор отдельное блокирующее окно,
        он вызывается прямо отсюда."""
        level = edit_level(parent=self.app.root, themes=self.app.themes)
        if level is not None:
            self.app.show(GameScreen, level, "свой уровень", self._return_here)
            
    def _random_level(self):
        name = library.random_name()
        if name is None:
            messagebox.showinfo("Библиотека пуста", f"В библиотеке нет уровней:\n{LIBRARY_DIR}",
                                parent=self.app.root)
            return
        play_library_level(self.app, name, back=self._return_here)

    def _pick_level(self):
        self.app.show(PickLevelScreen, self._return_here)