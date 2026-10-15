from datetime import datetime
from parser import choose_parsing
from solver import solve 
from runner import execute_solution

def main():
    
    levels_info = choose_parsing()

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
            execution = int(input())
            if execution==1:
                execute_solution(reshenie)
            
        else:
            print("=====================================================================================")
            print(f"Уровень: {name}")
            print("Решений не найдено")
        
if __name__ == "__main__":
    main()
        