class Styler:
    """Запоминает виджеты по ролям и перекрашивает их по теме.
    Роли: "bg" (только фон), "label" (фон и цвет текста),
    "button" (кнопка), "tool" (кнопка-переключатель палитры)."""

    def __init__(self):
        self._items = []

    def add(self, widget, role):
        self._items.append((widget, role))
        return widget

    def apply(self, theme):
        ui = theme.ui
        for widget, role in self._items:
            if role == "bg":
                widget.configure(bg=ui["window_bg"])
            elif role == "label":
                widget.configure(bg=ui["window_bg"], fg=ui["button_fg"])
            elif role in ("button", "tool"):
                options = dict(bg=ui["button_bg"], fg=ui["button_fg"],
                               activebackground=ui["panel_bg"],
                               activeforeground=ui["button_fg"],
                               disabledforeground=ui["panel_bg"])
                if role == "tool":
                    options["selectcolor"] = ui.get("selected_bg", "#2f6fb0")
                widget.configure(**options)
            elif role == "entry":
                widget.configure(bg=ui["button_bg"], fg=ui["button_fg"],
                                 insertbackground=ui["button_fg"],
                                 disabledbackground=ui["panel_bg"],
                                 disabledforeground=ui["panel_bg"])
            elif role == "list":
                widget.configure(bg=ui["button_bg"], fg=ui["button_fg"],
                                 selectbackground=ui.get("selected_bg", "#2f6fb0"),
                                 selectforeground=ui["button_fg"])