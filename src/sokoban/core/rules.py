from core.state import State
import collections

DIRECTIONS = {
    "Up": (-1,0),
    "Right": (0,1),
    "Down": (1,0),
    "Left": (0,-1)
    }

def apply_move(state : State , dx , dy):
    newx = state.player_pos[0] + dx 
    newy = state.player_pos[1] + dy 
    new_player_pos = (newx,newy)
                
    if new_player_pos in state.walls:
        return None 
        
    new_boxes = set(state.boxes)        
    if new_player_pos in state.boxes:
        new_box_x = newx + dx
        new_box_y = newy + dy 
        new_box_pos = (new_box_x, new_box_y)
                    
        if new_box_pos in state.walls or new_box_pos in state.boxes:
            return None 
        
        new_boxes = (state.boxes - {new_player_pos}) | {new_box_pos}
    else:
        new_boxes = state.boxes
        
    new_state = State(new_player_pos,state.walls,new_boxes,state.goals)
    return new_state


def is_accessible(state, target):
    """Может ли игрок дойти до target, НЕ двигая коробки. Возвращает (bool, dist)."""
    if target in state.walls or target in state.boxes:
        return (False, -1)
    if state.player_pos == target:
        return (True, 0)

    visited = {state.player_pos: 0}
    queue = collections.deque([state.player_pos])
    while queue:
        cx, cy = queue.popleft()
        d = visited[(cx, cy)]
        for dx, dy in DIRECTIONS.values():
            n = (cx + dx, cy + dy)
            if n in visited or n in state.walls or n in state.boxes:
                continue
            visited[n] = d + 1
            if n == target:
                return (True, d + 1)
            queue.append(n)
    return (False, -1)