from core.heuristics import heuristic
from core.deadlocks import is_deadlock
from core.state import matrix_to_state
from core.rules import apply_move, DIRECTIONS
import heapq

def solve(level):
    start_state = matrix_to_state(level)

    
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
