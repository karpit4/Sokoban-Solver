from datetime import datetime
from console import choose_parsing
from core.solver import solve
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


def main():
    themes = ThemeManager()

    action = choose_action()
    levels_info = choose_parsing(themes)
    levels_info = confirm_levels(
        levels_info, themes,
        edit_callback=lambda m, p: edit_level(m, p, themes))
    if not levels_info:
        print("Нет подтверждённых уровней")
        return

    if action == "1":
        solve_levels(levels_info)
    else:
        play_levels(levels_info, themes)


if __name__ == "__main__":
    main()