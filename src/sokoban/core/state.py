class State:
    """Основной класс, с которым мы работаем. Состояние поля в данный момент"""
    def __init__(self,player,walls,boxes,goals):
        self.player_pos = player
        self.walls = frozenset(walls)  #множества кортежей, обозначающие координаты соотв. элементов
        self.boxes = frozenset(boxes)
        self.goals = frozenset(goals)
        
    def __hash__(self):
        return hash((self.player_pos, self.boxes))
    
    def __lt__(self, other):
        """
        Метод для сравнения состояний
        """
        return hash(self) < hash(other)
    
    def __eq__(self, other):
        return (self.player_pos == other.player_pos and 
                self.boxes == other.boxes)

    
    def is_goal(self):
        '''Функция возвращает True, если все коробки стоят по местам.'''
        return self.boxes == self.goals

def matrix_to_state(matrix):
    """Принимает матрицу уровня (как возвращают parse, parse_txt и конструктор)
    и возвращает соответствующий State.
    Можно также вручную нарисовать поле списком списков, соблюдая обозначения из Colors."""
    walls, boxes, goals = [], [], []
    player = None

    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if cell == "#":
                walls.append((i, j))
            elif cell == "B":
                boxes.append((i, j))
            elif cell == "P":
                player = (i, j)
            elif cell == "X":
                goals.append((i, j))
            elif cell == "G":
                goals.append((i, j))
                boxes.append((i, j))
            elif cell == "Q":
                player = (i, j)
                goals.append((i, j))

    return State(player, walls, boxes, goals)


def symbol_at(state: State, pos):
    """Символ клетки pos (как в Colors) с учётом цели под коробкой и игроком.
    Нужен, чтобы после хода перерисовать только изменившиеся клетки."""
    if pos in state.walls:
        return "#"
    on_goal = pos in state.goals
    if pos in state.boxes:
        return "G" if on_goal else "B"
    if pos == state.player_pos:
        return "Q" if on_goal else "P"
    return "X" if on_goal else "_"


def state_to_matrix(state: State):
    '''Принимает State и делает из него матрицу с обозначениями как в Colors.
    Размер поля берётся по стенам, поэтому уровень должен быть замкнут стенами.'''
    rows = max(x for x, _ in state.walls) + 1
    cols = max(y for _, y in state.walls) + 1
    return [[symbol_at(state, (i, j)) for j in range(cols)] for i in range(rows)]

def changed_cells(old: State, new: State):
    """Клетки, символ которых различается в двух состояниях одного уровня:
    старая и новая позиция игрока и клетки, где коробка появилась или исчезла.
    Стены и цели у состояний одного уровня одинаковы."""
    return {old.player_pos, new.player_pos} | (old.boxes ^ new.boxes)