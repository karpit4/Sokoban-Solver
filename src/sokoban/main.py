import time
from core.solve_job import CANCELLED, NO_SOLUTION, SOLVED, SolveJob
from console import choose_library_level, choose_parsing, choose_play_mode, choose_solution_action
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

def run_solver(level):
    """Запускает поиск решения в отдельном процессе и ждёт его конца.
    Ctrl+C отменяет поиск. Возвращает SolveJob."""
    job = SolveJob(level)
    print("Идёт поиск решения (Ctrl+C - отмена)...")
    try:
        while not job.poll():
            time.sleep(0.2)
    except KeyboardInterrupt:
        job.cancel()
    return job


def solve_levels(levels_info, themes):
    for n, (name, level) in enumerate(levels_info):
        job = run_solver(level)

        print("=====================================================================================")
        print(f"Уровень: {name}")
        if job.status == SOLVED:
            seconds = int(job.solver_time)
            print(f"Решение найдено. Ходов: {len(job.path)}")
            print(f"Затрачено {seconds // (60*60)} часов {(seconds//60)%60} минут и {seconds%60} секунд")
            action = choose_solution_action()
            if action == "1":
                execute_solution(job.path)
            elif action == "2":
                play_level(level, f"{name}: решение солвера", themes=themes, solution=job.path)
        elif job.status == NO_SOLUTION:
            print("Решений не найдено")
        elif job.status == CANCELLED:
            print("Поиск отменён")
            if n < len(levels_info) - 1:
                print("Перейти к следующему уровню? 1 - да, 0 - нет")
                if input().strip() != "1":
                    break
        else:
            print(f"Ошибка при решении: {job.error}")

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
            levels_info = [("свой уровень", level)]
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

    levels_info, needs_confirmation = choose_parsing(themes)
    if needs_confirmation:
        levels_info = confirm_levels(
            levels_info, themes,
            edit_callback=lambda m, p: edit_level(m, p, themes))
    if not levels_info:
        print("Нет подтверждённых уровней")
        return
    solve_levels(levels_info, themes)

if __name__ == "__main__":
    main()