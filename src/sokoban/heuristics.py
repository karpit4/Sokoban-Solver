from state import State 

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
