from levels.loaders import VALID_CHARS, normalize, parse, parse_txt
from levels import library
from paths import LIBRARY_DIR

def choose_solution_action():
    print("Что сделать с решением?")
    print("\n 1 - Ввести решение в игру через pyautogui (программа сама нажмёт клавиши в активном окне) \n 2 - Показать решение в окне программы \n 0 - Ничего \n")
    while True:
        answer = input().strip()
        if answer in ("0", "1", "2"):
            return answer
        print("Некорректный ввод")

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
    return normalize(field)


def choose_theme(themes):
    """Показывает список тем и применяет выбранную (пустой ввод оставляет текущую)."""
    names = themes.names()
    if not names:
        print("В папке textures нет тем")
        return
    print("Доступные темы:")
    for i, name in enumerate(names, start=1):
        mark = " (текущая)" if name == themes.name else ""
        print(f" {i} - {name}{mark}")
    print("Введите номер или название темы (пустая строка - оставить текущую)")
    while True:
        answer = input().strip()
        if not answer:
            return
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            chosen = names[int(answer) - 1]
        elif answer in names:
            chosen = answer
        else:
            print("Такой темы нет, попробуйте ещё раз")
            continue
        themes.set(chosen)
        print(f"Выбрана тема: {chosen}")
        return

def choose_play_mode():
    print("====================================================================================")
    print("Во что играть")
    print("\n 1 - Свой уровень (конструктор) \n 2 - Случайный уровень \n 3 - Выбрать уровень из библиотеки \n 0 - Выход \n")
    while True:
        answer = input().strip()
        if answer in ("1", "2", "3", "0"):
            return answer
        print("Некорректный ввод")


def choose_library_level():
    """Поиск по части названия. Возвращает название уровня или None (назад)."""
    names = library.list_names()
    if not names:
        print(f"В библиотеке нет уровней: {LIBRARY_DIR}")
        return None
    print(f"Уровней в библиотеке: {len(names)}")
    print("Введите часть названия (пустая строка - показать все, 0 - назад)")
    while True:
        query = input().strip()
        if query == "0":
            return None
        matches = library.find(query)
        if not matches:
            print("Ничего не найдено, попробуйте ещё раз")
            continue
        exact = [name for name in matches if name.lower() == query.lower()]
        if exact or len(matches) == 1:
            chosen = (exact or matches)[0]
            print(f"Выбран уровень: {chosen}")
            return chosen
        for i, name in enumerate(matches, start=1):
            print(f" {i} - {name}")
        print("Введите номер уровня (0 - новый поиск)")
        while True:
            answer = input().strip()
            if answer == "0":
                break
            if answer.isdigit() and 1 <= int(answer) <= len(matches):
                chosen = matches[int(answer) - 1]
                print(f"Выбран уровень: {chosen}")
                return chosen
            print("Некорректный ввод")
        print("Введите часть названия (пустая строка - показать все, 0 - назад)")


def choose_parsing(themes=None) -> list[tuple[str, list]]:
    print("====================================================================================")
    print("Выберите способ считать уровень")
    print("\n 1 - Считать имена файлов (png,jpg) через пробел \n 2 - Считать уровень построчно \n 3 - Считать уровни построчно из .txt \n 4 - Считать уровень из конструктора ")
    if themes is not None:
        print(" 5 - Сменить тему оформления \n")
    while True:
        mode = input()
        if mode == "1":
            levels = []
            files = input().split()
            for file_name in files:
                try:
                    level = parse(file_name)
                except:
                    print(f'Файл "{file_name}" не найден')
                    continue
                levels.append((file_name, level))
            return levels

        if mode == "2":
            print("================================Условные обозначения================================")
            print("\n# - стена \n_ - пустая клетка \nB - коробка \nP - игрок \nX - конечная клетка \nG - коробка на конечной клетке \nQ - игрок на конечной клетке \n")
            print("Введите уровень построчно, закончите, введя 0")
            return [("manual level", parse_from_input())]

        if mode == "3":
            print("================================Условные обозначения================================")
            print("\n# - стена \n_ - пустая клетка \nB - коробка \nP - игрок \nX - конечная клетка \nG - коробка на конечной клетке \nQ - игрок на конечной клетке \n")
            print("====================================Формат файла====================================")
            print("\nТекстовый файл (.txt), уровень записан построчно символами выше.")
            print("Разные уровни разделяются пустой строкой")
            print("Введите имена .txt файлов через пробел")
            levels = []
            for file_name in input().split():
                parsed = parse_txt(file_name)
                for i, level in enumerate(parsed, start=1):
                    if len(parsed) == 1:
                        levels.append((file_name, level))
                    else:
                        levels.append((f"{file_name} #{i}", level))
            return levels

        if mode == "4":
            from gui.editor_window import edit_level
            levels = []
            while True:
                level = edit_level(themes=themes)
                if level is not None:
                    levels.append((f"constructor #{len(levels) + 1}", level))
                print("Создать ещё один уровень? 1 - да, 0 - нет")
                if input().strip() != "1":
                    break
            return levels
        if mode == "5" and themes is not None:
            choose_theme(themes)
            return choose_parsing(themes)

        print("Некорректный ввод")