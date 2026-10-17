class SolutionPlayback:
    """Пошаговое проигрывание решения (списка направлений, как возвращает solve)
    в партии GameSession. Без интерфейса: таймер и кнопки остаются за окном."""

    def __init__(self, session, moves):
        self.session = session
        self.moves = list(moves)
        self.index = 0                 # сколько ходов решения уже сделано

    @property
    def total(self):
        return len(self.moves)

    @property
    def finished(self):
        return self.index >= len(self.moves) or self.session.is_won

    def step(self):
        """Делает следующий ход решения. Возвращает изменившиеся клетки.
        Пустое множество означает, что играть больше нечего."""
        if self.finished:
            return set()
        cells = self.session.move(self.moves[self.index])
        self.index += 1
        if not cells:                  # решение не подходит к этому уровню: останавливаемся
            self.index = len(self.moves)
        return cells