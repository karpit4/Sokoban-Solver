from core.heuristics import heuristic
from core.deadlocks import is_deadlock
from core.state import State
from core.rules import apply_move, DIRECTIONS
import heapq

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
            elif level[i][j] == "Q":
                player = (i,j)
                goals.append((i,j))
                
    Ans = State(player,walls,boxes,goals)
    return Ans

def solve(level):
    start_state = matrix_to_states(level)

    
    minheap = []
    start_g = 0
    start_h = heuristic(start_state)
    start_f = start_g + start_h
    visited = set()
    
    proc = (start_f, start_g, start_state, [])
    
    heapq.heappush(minheap,proc)
    visited.add(start_state)
    
    
    while minheap:
        f,g,state,path = heapq.heappop(minheap)
        
        if state.is_goal():
            return path 
        
        for move,(dx,dy) in DIRECTIONS.items():
            new_state = apply_move(state,dx,dy)
            if not new_state:
                continue
            
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
