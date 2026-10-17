from pathlib import Path
from PIL import Image
import numpy as np

Colors = {
    128: "#", 0: "_", 255: "_", 206: "B",
    214: "P", 219: "X", 193: "G",
}

def parse(name):
    '''Принимает имя файла с картинкой, возвращает матрицу с условными обозначениями
    как в Colors'''
    image = Image.open(name)
    image_bw = image.convert("L")
    matrix = np.array(image_bw)
    H, W = matrix.shape
    field = [[' '] * (W // 30) for _ in range(H // 30)]
    i, j = 0, 0
    for strok in range(14, H, 30):
        for stolb in range(14, W, 30):
            field[i][j] = Colors.get(int(matrix[strok][stolb]), "?")
            j += 1
        j = 0
        i += 1
    return field


def save_txt(field, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for row in field:
            f.write("".join(row) + "\n")


def convert_folder(folder: str):
    folder = Path(folder)
    png_files = sorted(folder.glob("*.png"))  # сортировка — чтобы порядок был предсказуем
    for png in png_files:
        field = parse(str(png))
        txt = png.with_suffix(".txt")          # level_name.png -> level_name.txt
        save_txt(field, txt)
        print(f"{png.name} -> {txt.name}")


if __name__ == "__main__":
    convert_folder(".")