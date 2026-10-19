from tkinter import messagebox

from gui.game_window import GameFrame
from gui.screens.base import Screen
from levels import library
from levels.validation import validate


class GameScreen(Screen):
    """Экран игры. back() вызывается по кнопке «Выйти».
    solution: список ходов солвера для автоматического показа (необязательно)."""

    def __init__(self, master, app, matrix, name, back, solution=None):
        super().__init__(master, app)
        self.game = GameFrame(self, matrix, name, app.themes,
                              on_exit=lambda won, moves: back(),
                              solution=solution, on_settings=self._open_settings)
        self.game.pack()

    def focus_set(self):
        self.game.focus_set()          # клавиши ловит игровой Frame

    def on_hide(self):
        self.game.suspend()            # показ решения не должен идти, пока открыты настройки

    def on_show(self):
        self.game.resume()

    def _open_settings(self):
        self.app.open_settings()

def play_library_level(app, name, back):
    """Загружает уровень из библиотеки и открывает игру.
    Если файл повреждён или уровень некорректен, показывает сообщение и возвращает False."""
    try:
        matrix = library.load(name)
    except (ValueError, OSError) as e:
        messagebox.showerror("Не удалось загрузить уровень", str(e), parent=app.root)
        return False
    issues = validate(matrix)
    if issues:
        text = "\n".join("• " + issue.message for issue in issues)
        messagebox.showerror("Уровень содержит ошибки", f'Уровень "{name}":\n{text}',
                             parent=app.root)
        return False
    app.show(GameScreen, matrix, name, back)
    return True