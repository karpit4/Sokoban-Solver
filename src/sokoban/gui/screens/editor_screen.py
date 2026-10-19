from gui.editor_window import EditorFrame
from gui.screens.base import Screen


class EditorScreen(Screen):
    """Экран конструктора. matrix: уровень для правки или None (новый).
    on_done(level) вызывается по «Готово» с матрицей без пустых краёв,
    on_cancel() по «Отмена»."""

    def __init__(self, master, app, matrix, on_done, on_cancel):
        super().__init__(master, app)
        self.editor = EditorFrame(self, matrix, app.themes, on_done, on_cancel,
                                  on_settings=app.open_settings)
        self.editor.pack()

    def focus_set(self):
        self.editor.focus_set()        # клавиши ловит сам конструктор