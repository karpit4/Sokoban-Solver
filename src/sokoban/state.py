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
    '''Принимает State и делает из него матрицу с условными обозначениями как в Colors. '''
    xs = [x[0] for x in state.walls]
    ys = [x[1] for x in state.walls]
    x_size = max(xs)
    y_size = max(ys)
    Matrix = [0]*(x_size+1)
    for row in range(len(Matrix)):
        Matrix[row] = [0] * (y_size+1)
    
    Matrix[state.player_pos[0]][state.player_pos[1]] = 'P'
    for x,y in state.walls:
        Matrix[x][y] = '#'
    
    for x,y in state.goals:
        Matrix[x][y] = 'X'
    
    for x,y in state.boxes:
        if Matrix[x][y] == 'X':
            Matrix[x][y] = 'G'
        else:
            Matrix[x][y] = 'B'
    
    for x in range(len(Matrix)):
        for y in range(len(Matrix[0])-1,-1,-1):
            if Matrix[x][y] == 0:
                if y == len(Matrix[0])-1:
                    Matrix[x][y] = ''
                elif Matrix[x][y+1] == '':
                    Matrix[x][y] = ''
                else:
                    Matrix[x][y] = '_'
        j = 0
        while Matrix[x][j] != '#':
            Matrix[x][j] = ''
            j += 1
    return Matrix




def Equal_states(first: State, second: State):
    '''Возвращает, равны ли два состояния'''
    return (first.player_pos == second.player_pos) and (first.boxes == second.boxes)
