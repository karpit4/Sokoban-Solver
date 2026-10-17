import tkinter as tk

from gui.app import set_root
from gui.screens.menu import MenuScreen
from gui.styling import Styler
from gui.theme import ThemeManager

MIN_WIDTH, MIN_HEIGHT = 520, 380


class App:
    """Главное окно программы: контейнер, в котором по очереди показываются экраны.
    Тема меняется в настройках."""

    def __init__(self, themes=None):
        self.root = tk.Tk()
        set_root(self.root)            # окна, которые берут get_root(), откроются поверх этого
        self.root.title("Sokoban")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.themes = themes or ThemeManager()
        self.styler = Styler()
        self.styler.add(self.root, "bg")
        self.screen = None

        self.container = self.styler.add(tk.Frame(self.root), "bg")
        self.container.pack(fill="both", expand=True)

        self.styler.apply(self.themes.theme)
        self.themes.subscribe(self.root, self._on_theme_change)

    def _on_theme_change(self, theme):
        self.styler.apply(theme)

    def show(self, screen_class, *args, **kwargs):
        """Заменяет текущий экран новым: screen_class(container, app, *args, **kwargs)."""
        screen = screen_class(self.container, self, *args, **kwargs)
        if self.screen is not None:
            self.screen.destroy()
        screen.styler.apply(self.themes.theme)
        screen.pack(fill="both", expand=True)
        screen.focus_set()
        self.screen = screen

    def run(self):
        self.show(MenuScreen)
        self._center()
        self.root.mainloop()

    def _center(self):
        """Ставит окно по центру экрана по горизонтали и выше центра по вертикали.
        Размер не задаётся, окно подстраивается под содержимое экрана."""
        self.root.update_idletasks()
        w = max(self.root.winfo_reqwidth(), MIN_WIDTH)
        h = max(self.root.winfo_reqheight(), MIN_HEIGHT)
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry(f"+{x}+{y}")