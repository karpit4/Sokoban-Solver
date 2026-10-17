from dataclasses import dataclass

PLAYER_SYMBOLS = {"P", "Q"}
BOX_SYMBOLS = {"B", "G"}
GOAL_SYMBOLS = {"X", "G", "Q"}


@dataclass
class Issue:
    message: str          # текст для пользователя
    cells: tuple = ()     # координаты (строка, столбец) для подсветки


def validate(matrix):
    """Проверяет только то, без чего солвер не сможет даже начать работу.
    Возвращает список Issue. Пустой список означает, что уровень можно подтверждать."""
    if not matrix or not any(matrix):
        return [Issue("Уровень пуст")]

    players, boxes, goals, unknown = [], [], [], []
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell in PLAYER_SYMBOLS:
                players.append((i, j))
            if cell in BOX_SYMBOLS:
                boxes.append((i, j))
            if cell in GOAL_SYMBOLS:
                goals.append((i, j))
            if cell == "?":
                unknown.append((i, j))

    issues = []
    if unknown:
        issues.append(Issue(f"Нераспознанные клетки: {len(unknown)}", tuple(unknown)))
    if len(players) != 1:
        issues.append(Issue(f"Игрок должен быть ровно один, сейчас {len(players)}", tuple(players)))
    if len(boxes) != len(goals):
        issues.append(Issue(f"Коробок {len(boxes)}, а целей {len(goals)}: их должно быть поровну",
                            tuple(boxes + goals)))
    return issues