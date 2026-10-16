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

def state_to_matrix(state: State):
    '''Принимает State и делает из него матрицу с обозначениями как в Colors.'''
    rows = max(x for x, _ in state.walls) + 1
    cols = max(y for _, y in state.walls) + 1
    Matrix = [["_"] * cols for _ in range(rows)]

    for x, y in state.goals:
        Matrix[x][y] = "X"
    for x, y in state.walls:
        Matrix[x][y] = "#"
    for x, y in state.boxes:
        Matrix[x][y] = "G" if (x, y) in state.goals else "B"
    px, py = state.player_pos
    Matrix[px][py] = "Q" if (px, py) in state.goals else "P"
    return Matrix




def Equal_states(first: State, second: State):
    '''Возвращает, равны ли два состояния'''
    return (first.player_pos == second.player_pos) and (first.boxes == second.boxes)
