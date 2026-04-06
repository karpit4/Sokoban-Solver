from PIL import Image
import numpy as np
import heapq 
import time 
import pyautogui
from datetime import datetime

#Эта версия пока наиболее эффективна, используется алгоритм A*, все функции далее также описаны,
# возможна доработка или добавления эвристик, можно попробовать поиграть с коэффициентами при переменных в эвристике
# Солвер решает все уровни miniban с сайта logic-games-spb, в среднем за ~30 сек. Также решает original Rabbit 1 с того же сайта,
# но на это требуется уже около семи минут. На других уровнях не пробовал потому, что занимает слишком долго.#

Colors = {128:"#",      #стена
          0:"",         #вне поля
          255:"_",      #пустая клетка
          206:"B",      #коробка
          214:"P",      #игрок
          219: "X",     #конечная клетка
          193: "G"}     #коробка на конечной клетке

def parse(name):
    '''Принимает имя файла с картинкой, возвращает матрицу с условными обозначениями
    как в Colors'''
    image = Image.open(name)
    image_bw = image.convert("L")
    matrix = np.array(image_bw)
    H, W = matrix.shape  # Размерность (высота, ширина)
    field = [0]*(H//30) 
    for i in range(len(field)):
        field[i] = [' ']*(W//30)
    i,j= 0 ,0
    for strok in range(14,(H),30):
        for stolb in range(14,W,30):
            field[i][j] = (Colors[matrix[strok][stolb]])
            j+=1
        j=0
        i+=1
    return field 

def matrix_to_states(matrix):
    """Подаем сюда матрицу, полученную при помощи функции parse. На выходе получаем переменную типа State, соответствующую данной матрице
        Можно также вручную нарисовать поле при помощи списка списков, но строго соблюдая обозначения из Colors."""
    level = matrix
    walls,boxes,goals = [],[],[]
    player = 0

    for i in range(len(level)): #заполняем walls,boxes,goals, player для инициализации State
        for j in range(len(level[0])):
            if level[i][j] == "#":
                walls.append((i,j))
            elif level[i][j] == "B":
                boxes.append((i,j))
            elif level[i][j] == "P":
                player = (i,j)
            elif level[i][j] == "X":
                goals.append((i,j))
            elif level[i][j] == "G":
                goals.append((i,j))
                boxes.append((i,j))
    Ans = State(player,walls,boxes,goals)
    return Ans

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

def heuristic(state: State):
    """
    Эвристическая функция для алгоритма A*.
    Оценивает, насколько текущее состояние близко к целевому.\n
    !!Фактически, возвращает сумму расстояний от каждой коробки до ближайшей к ней цели!!\n
    +расстояние от игрока до каждой коробки, которая не на цели\n
    -количество коробок на целях
    """
    if not state.boxes:
        return 0
        
    total_distance = 0
    player_distance = 0
    cnt_boxes_on_goals = 0
    
    for box in state.boxes:
        
        min_dist = float('inf')  
        for goal in state.goals:
            
            dist = abs(box[0] - goal[0]) + abs(box[1] - goal[1])

            if dist < min_dist:
                min_dist = dist
                
        if min_dist != 0 : #если коробка не на цели, добавляем расстояние от нее до игрока
            player_distance += abs(box[0] - state.player_pos[0]) + abs(box[1] - state.player_pos[1])
        else:
            cnt_boxes_on_goals += 1 #если на цели, добавляем в счетчик
        
        total_distance += min_dist
    return (total_distance)*3 + (player_distance)*2 - (cnt_boxes_on_goals)**2

def is_pomehi(state: State, coordinates: list):
    '''Принимает состояние и список с кортежами координат объектов. Выводит True, если все объекты - стена либо коробка не на месте. False иначе'''
    for obj in coordinates:
        if obj not in state.walls and obj not in state.boxes:
            return False 
        elif obj in state.walls and obj in state.goals:
            return False 
    return True 

def is_hard_deadlock(state: State, box):
    '''Проверяет несколько более изощеренных тупиков \n
        True - тупик, False - не тупик '''
    x,y = box 
    var1 = [(x-1,y),(x,y+1),(x-2,y+1),(x-1,y+2),(x-2,y+2)]
    if is_pomehi(state, var1):
        return True 
    var2 = [(x+1,y),(x,y+1),(x+1,y+2),(x+2,y+1),(x+2,y+2)] 
    if is_pomehi(state, var2):
        return True 
    return False 

def is_deadlock(state: State):
    """Подаётся состояние, выводится True если тупик, False если не тупик"""
    for box in state.boxes:
        if box not in state.goals:
            x,y = box
            nleft,nup,nright,ndown = (x,y-1),(x-1,y),(x,y+1),(x+1,y)
            if (nleft in state.walls and nup in state.walls) or (nup in state.walls and nright in state.walls) or (nright in state.walls and ndown in state.walls) or (ndown in state.walls and nleft in state.walls):
                return True  #коробка в углу
            else:
                #   BB      WW
                #   BB или  WB и все повороты
                nleft_up,nright_up,nright_down, nleft_down = (x-1,y-1),(x-1,y+1),(x+1,y+1),(x+1,y-1)
                if is_pomehi(state,[nleft,nleft_up,nup]):
                        return True
                if is_pomehi(state,[nup,nright_up,nright]):
                        return True
                if is_pomehi(state,[nright,nright_down,ndown]):
                        return True
                if is_pomehi(state,[ndown,nleft_down,nleft]):
                        return True
            
            if is_hard_deadlock(state,box):
                return True  
            
    return False


def solve(start_state):
    dirs = {
        "Up": (-1,0),
        "Right": (0,1),
        "Down": (1,0),
        "Left": (0,-1)
    }
    
    minheap = []
    start_g = 0
    start_h = heuristic(start_state)
    start_f = start_g + start_h
    visited = set()
    cnt = 0
    
    proc = (start_f, start_g, start_state, [])
    
    heapq.heappush(minheap,proc)
    visited.add(start_state)
    
    
    while minheap:
        f,g,state,path = heapq.heappop(minheap)
        
        if state.is_goal():
            return path 
        
        for move,(dx,dy) in dirs.items():
            newx = state.player_pos[0] + dx 
            newy = state.player_pos[1] + dy 
            new_player_pos = (newx,newy)
            
            if new_player_pos in state.walls:
                continue
            
            new_boxes = set(state.boxes)
            if new_player_pos in state.boxes:
                new_box_x = newx + dx
                new_box_y = newy + dy 
                new_box_pos = (new_box_x, new_box_y)
                
                if new_box_pos in state.walls or new_box_pos in state.boxes:
                    continue
                
                new_boxes.remove(new_player_pos)
                new_boxes.add(new_box_pos)
            new_state = State(new_player_pos,state.walls,new_boxes,state.goals)
            
            if is_deadlock(new_state):
                continue
            
            if new_state not in visited:
                visited.add(new_state)
                newg = g + 0.3
                newh = heuristic(new_state)
                newf = newg + newh 
                
                new_path = path + [move]
                
                heapq.heappush(minheap,(newf,newg,new_state,new_path))
    return None   




print("Введите название файла")

files = [input()]
start_time = datetime.now()
for file_name in files:
    level = parse(file_name)
    Start_state = matrix_to_states(level)
    reshenie = solve(Start_state)
    if reshenie is not None:
        
        end_time = datetime.now()
        diff = end_time - start_time
        
        print(f"Решение найдено. Ходов: {len(reshenie)}")
        print(f"Затрачено {diff.seconds // (60*60)} часов {(diff.seconds//60)%60} минут и {diff.seconds%60} секунд")
        print("Введите что-нибудь, чтобы применить решение")
        input()
        print("Через 5 секунд программа запустится и произведет последовательность команд")
        for i in range(5):
            time.sleep(1)
            print(5-i)
        
        print(reshenie)
        pyautogui.press(reshenie)
        
    else:
        print("Решений не найдено")