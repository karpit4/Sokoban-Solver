from PIL import Image
import numpy as np

VALID_CHARS = set("#_BPXGQ")
Colors = {128:"#",      #стена
          0:"_",         #вне поля
          255:"_",      #пустая клетка
          206:"B",      #коробка
          214:"P",      #игрок
          219: "X",     #конечная клетка
          193: "G"}     #коробка на конечной клетке
#Q - игрок на цели

def normalize(field):
    '''Выравнивает строки по длине, добивая короткие стенами'''
    if field:
        width = max(len(row) for row in field)
        for row in field:
            row.extend(['#'] * (width - len(row)))
    return field

def parse_txt(name):
    '''Принимает имя .txt файла, где уровни заданы построчно и разделены
    пустой строкой. Возвращает список уровней, каждый уровень - матрица
    с условными обозначениями, как в parse(name)'''
    levels = []
    field = []
    with open(name, encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                # пустая строка закрывает текущий уровень
                if field:
                    levels.append(normalize(field))
                    field = []
                continue
            if not set(line) <= VALID_CHARS:
                raise ValueError(
                    f"{name}, строка {line_number}: недопустимые символы в '{line}'"
                )
            field.append(list(line))
    if field:  # последний уровень, если файл не заканчивается пустой строкой
        levels.append(normalize(field))
    return levels

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
            field[i][j] = Colors.get(int(matrix[strok][stolb]), "?")
            j+=1
        j=0
        i+=1
    return field 
