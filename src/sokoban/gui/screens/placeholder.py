from gui.screens.base import Screen


class PlaceholderScreen(Screen):
    """Заглушка для разделов, которые ещё не перенесены в главное окно.
    back() вызывается по кнопке «Назад»."""

    def __init__(self, master, app, title, back):
        super().__init__(master, app)
        self.configure(padx=60, pady=40)
        self.label(self, text=title, font=("Segoe UI", 20, "bold")).pack(pady=(0, 12))
        self.label(self, text="Этот раздел ещё в разработке",
                   font=("Segoe UI", 11)).pack(pady=(0, 24))
        self.button(self, "Назад", back, width=16).pack()