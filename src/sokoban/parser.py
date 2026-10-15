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

VALID_CHARS = set("#_BPXG")

def parse_from_input():
    '''Читает уровень построчно из консоли, заканчивается на 0.
    Возвращает матрицу с условными обозначениями, как parse(name)'''
    field = []
    while True:
        line = input().strip()
        if line == "0":
            break
        if not line:
            continue  # пропускаем пустые строки
        if not set(line) <= VALID_CHARS:
            print("Недопустимые символы, введите строку заново")
            continue
        field.append(list(line))  # строка -> список символов

    # выравниваем строки по длине (как в parse, где поле прямоугольное)
    if field:
        width = max(len(row) for row in field)
        for row in field:
            row.extend(['#'] * (width - len(row)))
    return field

def choose_parsing():
    print("Выберите способ ввести уровень")
    print("\n 1 - Ввести имена файлов через пробел \n 2 - Ввести уровень построчно")

    mode = int(input())
    if mode == 1:
        levels = []
        files = input().split()
        for file_name in files:
            level = parse(file_name)
            levels.append((file_name, level))
        return levels

    if mode == 2:
        print("==================Условные обозначения==================")
        print("\n# - стена \n_ - пустая клетка \nB - коробка \nP - игрок \nX - конечная клетка \nG - коробка на конечной клетке ")
        print("Введите уровень построчно, закончите, введя 0")
        return [("manual level", parse_from_input())]
    
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

