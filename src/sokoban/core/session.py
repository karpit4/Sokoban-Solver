from core.rules import DIRECTIONS, apply_move, find_path
from core.state import changed_cells, matrix_to_state


class GameSession:
    """Партия в Сокобан: текущее состояние, история ходов и отмена.
    Без интерфейса и ввода-вывода, поэтому подходит и для окна игры,
    и для проигрывания решения солвера.

    Все методы, меняющие партию (move, walk_to, undo, restart), возвращают множество клеток,
    символ которых изменился: окну достаточно перерисовать только их через
    board.set_cell(i, j, symbol_at(session.state, (i, j)))."""

    def __init__(self, matrix):
        self.initial = matrix_to_state(matrix)
        self.state = self.initial
        self._history = []        # тройки (направление, состояние до хода, группа)
        self._next_group = 0      # номер группы для переходов по клику

    # ---------- информация ----------

    @property
    def moves(self):
        """Сделанные ходы в порядке выполнения: ["Up", "Left", ...]."""
        return [direction for direction, _, _ in self._history]

    @property
    def move_count(self):
        return len(self._history)

    @property
    def is_won(self):
        return self.state.is_goal()

    @property
    def can_undo(self):
        return bool(self._history)

    # ---------- действия ----------

    def _step(self, direction, group=None):
        """Один ход. Возвращает False, если ход невозможен."""
        dx, dy = DIRECTIONS[direction]
        new_state = apply_move(self.state, dx, dy)
        if new_state is None:
            return False
        self._history.append((direction, self.state, group))
        self.state = new_state
        return True

    def move(self, direction):
        """direction: "Up", "Down", "Left" или "Right" (ключи DIRECTIONS).
        Возвращает изменившиеся клетки. Пустое множество означает, что хода не было:
        на пути стена или коробка, которую нельзя сдвинуть, либо уровень уже пройден."""
        if direction not in DIRECTIONS:
            raise ValueError(f"Неизвестное направление: {direction!r}")
        if self.is_won:
            return set()
        before = self.state
        if not self._step(direction):
            return set()
        return changed_cells(before, self.state)

    def walk_to(self, target):
        """Ведёт игрока в клетку target кратчайшим путём, не двигая коробки.
        Каждый шаг пути считается ходом, но отмена откатывает весь переход разом.
        Возвращает изменившиеся клетки. Пустое множество означает, что перехода не было:
        клетка недостижима, это стена или коробка, игрок уже там, либо уровень пройден."""
        if self.is_won:
            return set()
        path = find_path(self.state, target)
        if not path:                  # None (недостижима) или [] (игрок уже там)
            return set()
        before = self.state
        group = self._next_group
        self._next_group += 1
        for direction in path:
            self._step(direction, group)
        return changed_cells(before, self.state)

    def undo(self):
        """Отменяет последний ход (или весь последний переход по клику).
        Возвращает изменившиеся клетки."""
        if not self._history:
            return set()
        _, previous, group = self._history.pop()
        if group is not None:
            while self._history and self._history[-1][2] == group:
                _, previous, _ = self._history.pop()
        cells = changed_cells(self.state, previous)
        self.state = previous
        return cells

    def restart(self):
        """Возвращает уровень к началу и очищает историю. Возвращает изменившиеся клетки."""
        cells = changed_cells(self.state, self.initial)
        self.state = self.initial
        self._history.clear()
        return cells