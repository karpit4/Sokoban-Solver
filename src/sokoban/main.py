from datetime import datetime
from console import choose_parsing
from core.solver import solve
from tools.runner import execute_solution
from gui.confirm_window import confirm_levels
from gui.editor_window import edit_level
from gui.theme import ThemeManager

def main():
    themes = ThemeManager()

    levels_info = choose_parsing(themes)
    levels_info = confirm_levels(
        levels_info, themes,
        edit_callback=lambda m, p: edit_level(m, p, themes))
    if not levels_info:
        print("Нет подтверждённых уровней")
        return

    for name,level in levels_info:
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
            if execution=="1":
                execute_solution(reshenie)
            
        else:
            print("=====================================================================================")
            print(f"Уровень: {name}")
            print("Решений не найдено")
        
if __name__ == "__main__":
    main()
        