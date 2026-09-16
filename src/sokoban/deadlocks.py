from state import State 

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
