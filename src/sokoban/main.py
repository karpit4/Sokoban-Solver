import os
from datetime import datetime
from parser import choose_parsing
from solver import solve
from runner import execute_solution
from gui.confirm_window import confirm_levels
from gui.editor_window import edit_level
from gui.theme import Theme, TEXTURES_DIR, list_themes
from gui.app import get_root

def choose_theme(current):
    """Показывает список тем и возвращает название выбранной (или текущей)."""
    themes = list_themes()
    if not themes:
        print("В папке textures нет тем")
        return current
    print("Доступные темы:")
    for i, name in enumerate(themes, start=1):
        mark = " (текущая)" if name == current else ""
        print(f" {i} - {name}{mark}")
    print("Введите номер или название темы (пустая строка - оставить текущую)")
    while True:
        answer = input().strip()
        if not answer:
            return current
        if answer.isdigit() and 1 <= int(answer) <= len(themes):
            chosen = themes[int(answer) - 1]
        elif answer in themes:
            chosen = answer
        else:
            print("Такой темы нет, попробуйте ещё раз")
            continue
        print(f"Выбрана тема: {chosen}")
        return chosen

def main():
    state = {"theme": "default"}
    cache = {}                      # название темы -> объект Theme

    def make_theme():
        """Тема, выбранная сейчас. Один объект на название, чтобы окна делили кэш."""
        name = state["theme"]
        if name not in cache:
            get_root()              # корень должен существовать до создания Theme
            cache[name] = Theme(os.path.join(TEXTURES_DIR, name))
        return cache[name]

    levels_info = choose_parsing(
        theme_change=lambda: state.update(theme=choose_theme(state["theme"])),
        make_theme=make_theme)

    theme = make_theme()
    levels_info = confirm_levels(levels_info, theme=theme,
                                 edit_callback=lambda m, p: edit_level(m, p, theme))
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
        