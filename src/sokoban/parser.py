from state import State 
from PIL import Image
import numpy as np

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