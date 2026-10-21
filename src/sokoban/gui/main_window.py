import tkinter as tk

from gui.screens.menu import MenuScreen
from gui.screens.settings_screen import SettingsScreen
from gui.styling import Styler
from gui.theme import ThemeManager

MIN_WIDTH, MIN_HEIGHT = 520, 380
TASKBAR = 80          # запас снизу под панель задач


class App:
    """Главное окно программы: контейнер, в котором по очереди показываются экраны.
    show() заменяет экран новым, push() открывает экран поверх текущего, не уничтожая его,
    а pop() возвращает спрятанный экран. Тема меняется в настройках."""

    def __init__(self, themes=None):
        self.root = tk.Tk()
        self.root.title("Sokoban")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.themes = themes or ThemeManager()
        self.styler = Styler()
        self.styler.add(self.root, "bg")
        self.screen = None
        self._hidden = []              # экраны, спрятанные через push; возвращаются по pop
        self._size_frozen = False

        self.container = self.styler.add(tk.Frame(self.root), "bg")
        self.container.pack(fill="both", expand=True)

        self.styler.apply(self.themes.theme)
        self.themes.subscribe(self.root, self._on_theme_change)

    def _on_theme_change(self, theme):
        self.styler.apply(theme)

    # ---------- смена экранов ----------

    def show(self, screen_class, *args, **kwargs):
        """Заменяет текущий экран новым: screen_class(container, app, *args, **kwargs).
        Экраны, спрятанные через push, при этом отбрасываются."""
        screen = screen_class(self.container, self, *args, **kwargs)
        for hidden in self._hidden:
            hidden.destroy()
        self._hidden.clear()
        self._unfreeze_size()
        if self.screen is not None:
            self.screen.destroy()
        self._display(screen)
        self._keep_on_screen()

    def push(self, screen_class, *args, **kwargs):
        """Показывает экран поверх текущего. Текущий не уничтожается, а прячется со всем
        состоянием (рисунок, партия, позиция) и возвращается по pop().
        Размер окна на это время фиксируется, чтобы оно не прыгало."""
        current = self.screen
        screen = screen_class(self.container, self, *args, **kwargs)
        self._freeze_size()
        current.on_hide()
        current.pack_forget()
        self._hidden.append(current)
        self._display(screen)

    def pop(self):
        """Закрывает экран, открытый через push, и возвращает спрятанный."""
        if not self._hidden:
            return
        top = self.screen
        previous = self._hidden.pop()
        top.destroy()
        previous.pack(fill="both", expand=True)
        self.screen = previous
        if not self._hidden:
            self._unfreeze_size()
        previous.on_show()
        previous.focus_set()
        self._keep_on_screen()

    def open_settings(self):
        """Настройки поверх текущего экрана: после «Назад» всё остаётся на своих местах."""
        if not isinstance(self.screen, SettingsScreen):
            self.push(SettingsScreen, back=self.pop)

    def _display(self, screen):
        screen.styler.apply(self.themes.theme)
        screen.pack(fill="both", expand=True)
        screen.focus_set()
        self.screen = screen

    # ---------- размер и положение окна ----------

    def _freeze_size(self):
        """Фиксирует текущий размер окна, пока экран закрыт другим."""
        if not self._size_frozen:
            self.root.update_idletasks()
            self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")
            self._size_frozen = True

    def _unfreeze_size(self):
        """Возвращает окну размер по содержимому."""
        if self._size_frozen:
            self.root.geometry("")
            self._size_frozen = False

    def run(self):
        self.show(MenuScreen)
        self._center()
        self.root.mainloop()

    def _keep_on_screen(self):
        """Окно подстраивается под экран и растёт вправо и вниз от своего места.
        Большой экран (конструктор) мог бы уйти за край, поэтому окно сдвигается."""
        self.root.update_idletasks()
        w = max(self.root.winfo_reqwidth(), MIN_WIDTH)
        h = max(self.root.winfo_reqheight(), MIN_HEIGHT)
        x, y = self.root.winfo_x(), self.root.winfo_y()
        new_x = max(0, min(x, self.root.winfo_screenwidth() - w))
        new_y = max(0, min(y, self.root.winfo_screenheight() - h - TASKBAR))
        if (new_x, new_y) != (x, y):
            self.root.geometry(f"+{new_x}+{new_y}")

    def _center(self):
        """Ставит окно по центру экрана по горизонтали и выше центра по вертикали.
        Размер не задаётся, окно подстраивается под содержимое экрана."""
        self.root.update_idletasks()
        w = max(self.root.winfo_reqwidth(), MIN_WIDTH)
        h = max(self.root.winfo_reqheight(), MIN_HEIGHT)
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 3
        self.root.geometry(f"+{x}+{y}")