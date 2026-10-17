"""Работа с матрицей уровня без интерфейса: обрезка пустых краёв и сохранение в .txt."""

def trim(matrix):
    """Обрезает края, на которых нет ничего, кроме пола.
    Возвращает прямоугольную матрицу или [], если в ней нет ни одного объекта."""
    if not matrix:
        return []
    width = max(len(row) for row in matrix)
    rows = [list(row) + ["_"] * (width - len(row)) for row in matrix]

    filled_rows = [i for i, row in enumerate(rows) if any(c != "_" for c in row)]
    if not filled_rows:
        return []
    filled_cols = [j for j in range(width) if any(row[j] != "_" for row in rows)]

    top, bottom = filled_rows[0], filled_rows[-1]
    left, right = filled_cols[0], filled_cols[-1]
    return [row[left:right + 1] for row in rows[top:bottom + 1]]


def to_txt_lines(matrix):
    return ["".join(row) for row in trim(matrix)]

def save_txt(path, matrix):
    """Сохраняет один уровень в формате, который читает parse_txt."""
    if any("?" in row for row in matrix):
        raise ValueError("В уровне есть нераспознанные клетки (?), замените их перед сохранением")
    lines = to_txt_lines(matrix)
    if not lines:
        raise ValueError("Уровень пуст")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")