import time 
import pyautogui

def execute_solution(solution):
    print("Введите что-нибудь, чтобы применить решение")
    input()
    print("Через 5 секунд программа запустится и произведет последовательность команд")
    for i in range(5):
        time.sleep(1)
        print(5-i)
            
    print(solution)
    pyautogui.press(solution)