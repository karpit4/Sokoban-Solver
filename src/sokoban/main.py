from datetime import datetime
from parser import parse 
from parser import matrix_to_states
from solver import solve 
from runner import execute_solution

def main():
    print("Введите название файлов")
    files = input().split()

    start_time = datetime.now()

    for file_name in files:
        level = parse(file_name)
        Start_state = matrix_to_states(level)
        reshenie = solve(Start_state)
        if reshenie is not None:
            
            end_time = datetime.now()
            diff = end_time - start_time
            
            print("=====================================================================================")
            print(f"Уровень: {file_name}")
            print(f"Решение найдено. Ходов: {len(reshenie)}")
            print(f"Затрачено {diff.seconds // (60*60)} часов {(diff.seconds//60)%60} минут и {diff.seconds%60} секунд")
            execute_solution(reshenie)
            
        else:
            print("Решений не найдено")
        
if __name__ == "__main__":
    main()
        