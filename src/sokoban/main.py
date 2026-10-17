from datetime import datetime
from console import choose_library_level, choose_parsing, choose_play_mode
from core.solver import solve
from levels import library
from levels.validation import validate
from paths import LIBRARY_DIR
from tools.runner import execute_solution
from gui.confirm_window import confirm_levels
from gui.editor_window import edit_level
from gui.game_window import play_level
from gui.theme import ThemeManager


def choose_action():
    print("====================================================================================")
    print("Выберите действие")
    print("\n 1 - Решить уровень \n 2 - Играть \n")
    while True:
        answer = input().strip()
        if answer in ("1", "2"):
            return answer
        print("Некорректный ввод")


def solve_levels(levels_info):
    for name, level in levels_info:
        start_time = datetime.now()
        reshenie = solve(level)
        if reshenie is not None:

            end_time = datetime.now()
            diff = end_time - start_time

            print("=====================================================================================")
            print(f"Уровень: {name}")
            print(f"Решение найдено. Ходов: {len(reshenie)}")
            print(f"Затрачено {diff.seconds // (60*60)} часов {(diff.seconds//60)%60} минут и {diff.seconds%60} секунд")
            print(f"Чтобы применить решение введите 1. Иначе введите 0")
            execution = input()
            if execution == "1":
                execute_solution(reshenie)

        else:
            print("=====================================================================================")
            print(f"Уровень: {name}")
            print("Решений не найдено")


def play_levels(levels_info, themes):
    for n, (name, level) in enumerate(levels_info):
        won, moves = play_level(level, name, themes=themes)
        print("=====================================================================================")
        print(f"Уровень: {name}")
        print(f"Пройден. Ходов: {len(moves)}" if won else "Уровень не пройден")
        if not won and n < len(levels_info) - 1:
            print("Перейти к следующему уровню? 1 - да, 0 - нет")
            if input().strip() != "1":
                break


def pick_library_level(mode):
    """(название, матрица) из библиотеки или None, если выбрать не удалось.
    mode: "2" - случайный уровень, "3" - выбор по названию."""
    if mode == "2":
        name = library.random_name()
        if name is None:
            print(f"В библиотеке нет уровней: {LIBRARY_DIR}")
            return None
        print(f"Случайный уровень: {name}")
    else:
        name = choose_library_level()
        if name is None:
            return None
    try:
        matrix = library.load(name)
    except (ValueError, OSError) as e:
        print(e)
        return None
    issues = validate(matrix)
    if issues:
        print(f'Уровень "{name}" содержит ошибки, играть нельзя:')
        for issue in issues:
            print(" •", issue.message)
        return None
    return name, matrix


def play_menu(themes):
    """Выбор, во что играть. После каждой партии возвращается в это же меню."""
    while True:
        mode = choose_play_mode()
        if mode == "0":
            return
        if mode == "1":
            level = edit_level(themes=themes)
            if level is None:
                continue
            levels_info = confirm_levels(
                [("свой уровень", level)], themes,
                edit_callback=lambda m, p: edit_level(m, p, themes))
        else:
            picked = pick_library_level(mode)
            levels_info = [picked] if picked else []
        if levels_info:
            play_levels(levels_info, themes)


def main():
    themes = ThemeManager()

    if choose_action() == "2":
        play_menu(themes)
        return

    levels_info = choose_parsing(themes)
    levels_info = confirm_levels(
        levels_info, themes,
        edit_callback=lambda m, p: edit_level(m, p, themes))
    if not levels_info:
        print("Нет подтверждённых уровней")
        return
    solve_levels(levels_info)


if __name__ == "__main__":
    main()