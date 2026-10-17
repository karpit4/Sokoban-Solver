from core.heuristics import heuristic
from core.deadlocks import is_deadlock
from core.state import State
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
