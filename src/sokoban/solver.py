from heuristics import heuristic
from deadlocks import is_deadlock
from state import State 
import heapq 


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
