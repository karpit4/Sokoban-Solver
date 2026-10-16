import tkinter as tk

MIN_CELL = 16
MAX_CELL = 64


class BoardView(tk.Frame):
    """Виджет-сетка: рисует матрицу уровня на Canvas.
    Только отображение: клики привязывает окно, которое использует виджет
    (через board.canvas.bind и board.cell_at)."""

    def __init__(self, master, theme, max_width=None, max_height=None):
        super().__init__(master, bg=theme.ui["window_bg"])
        self.theme = theme
        # максимальный размер поля в пикселях (по умолчанию от размера экрана)
        self.max_width = max_width or int(self.winfo_screenwidth() * 0.6)
        self.max_height = max_height or int(self.winfo_screenheight() * 0.65)

        self.canvas = tk.Canvas(self, bg=theme.ui["window_bg"], highlightthickness=0)
        self.canvas.pack()

        self.matrix = []
        self.rows = 0
        self.cols = 0
        self.cell_size = MAX_CELL
        self._cell_ids = {}   # (строка, столбец) -> (id прямоугольника, id картинки)
        self._photos = {}     # (строка, столбец) -> PhotoImage (ссылки, чтобы их не удалил GC)

    # ---------- полная отрисовка ----------

    def set_matrix(self, matrix):
        """Рисует уровень с нуля. Вызывать при загрузке уровня или смене размера."""
        self.rows = len(matrix)
        self.cols = max((len(row) for row in matrix), default=0)
        # копия, дополненная до прямоугольника (недостающее считается «вне поля»)
        self.matrix = [list(row) + ["_"] * (self.cols - len(row)) for row in matrix]


        self.canvas.delete("all")
        self._cell_ids.clear()
        self._photos.clear()

        if self.rows == 0 or self.cols == 0:
            self.canvas.config(width=1, height=1)
            return

        self.cell_size = max(MIN_CELL, min(MAX_CELL,
                                           self.max_width // self.cols,
                                           self.max_height // self.rows))
        s = self.cell_size
        self.canvas.config(width=self.cols * s, height=self.rows * s)

        grid_color = self.theme.ui["grid_line"]
        for i in range(self.rows):
            for j in range(self.cols):
                x, y = j * s, i * s
                rect = self.canvas.create_rectangle(x, y, x + s, y + s, outline=grid_color)
                img = self.canvas.create_image(x, y, anchor="nw")
                self._cell_ids[(i, j)] = (rect, img)
                self._apply(i, j, self.matrix[i][j])
 
    def set_theme(self, theme):
        """Подставляет другую тему и перерисовывает поле.
        Подсветку ошибок после этого нужно нарисовать заново (highlight)."""
        self.theme = theme
        self.configure(bg=theme.ui["window_bg"])
        self.canvas.configure(bg=theme.ui["window_bg"])
        if self.matrix:
            self.set_matrix(self.matrix)


    # ---------- изменение одной клетки ----------

    def set_cell(self, i, j, symbol):
        """Меняет одну клетку. Возвращает True, если что-то изменилось."""
        if not (0 <= i < self.rows and 0 <= j < self.cols):
            return False
        if self.matrix[i][j] == symbol:
            return False   # при drag мышь часто остаётся в той же клетке
        self.matrix[i][j] = symbol
        self._apply(i, j, symbol)
        return True

    def _apply(self, i, j, symbol):
        rect, img = self._cell_ids[(i, j)]
        # прямоугольник есть всегда: он служит запасным вариантом без текстуры
        self.canvas.itemconfigure(rect, fill=self.theme.get_color(symbol))
        photo = self.theme.get_image(symbol, self.cell_size)
        self._photos[(i, j)] = photo
        self.canvas.itemconfigure(img, image=photo if photo is not None else "")

    # ---------- подсветка ошибок ----------

    def highlight(self, cells):
        """Красные рамки вокруг клеток (например, из Issue.cells)."""
        self.clear_highlight()
        s = self.cell_size
        color = self.theme.ui["error_outline"]
        for i, j in cells:
            if 0 <= i < self.rows and 0 <= j < self.cols:
                x, y = j * s, i * s
                self.canvas.create_rectangle(x + 1, y + 1, x + s - 1, y + s - 1,
                                             outline=color, width=3, tags="highlight")

    def clear_highlight(self):
        self.canvas.delete("highlight")

    # ---------- вспомогательное ----------

    def cell_at(self, x, y):
        """Пиксель холста -> (строка, столбец) или None, если вне поля.
        x, y берутся из event.x и event.y."""
        if self.cell_size <= 0:
            return None
        i, j = int(y // self.cell_size), int(x // self.cell_size)
        if 0 <= i < self.rows and 0 <= j < self.cols and x >= 0 and y >= 0:
            return (i, j)
        return None

    def get_matrix(self):
        """Копия текущей матрицы (с учётом изменений через set_cell)."""
        return [row[:] for row in self.matrix]