import csv
import multiprocessing as mp
import os
import re
import time
from datetime import datetime

from parser import parse
from solver import solve
from gui.validation import validate

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRAINING_DIR = os.path.join(PROJECT_DIR, "training")
RESULTS_DIR = os.path.join(PROJECT_DIR, "benchmarks")
TIME_LIMIT = 180          # секунд на один уровень
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def natural_key(name):
    """level2 раньше level10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name.lower())]


def worker(level, conn):
    """Выполняется в отдельном процессе: решает уровень и отправляет результат."""
    try:
        conn.send(("started",))            # импорты позади, родитель запускает таймер
        start = time.perf_counter()
        path = solve(level)
        elapsed = time.perf_counter() - start
        conn.send(("done", elapsed, None if path is None else len(path)))
    except BaseException as e:             # например MemoryError
        conn.send(("error", repr(e)))
    finally:
        conn.close()


def run_level(level):
    """Возвращает (статус, секунды, число ходов).
    Статусы: solved, no_solution, timeout, error."""
    recv, send = mp.Pipe(duplex=False)
    proc = mp.Process(target=worker, args=(level, send), daemon=True)
    proc.start()
    send.close()                           # в родителе конец для записи не нужен
    try:
        if not recv.poll(60) or recv.recv()[0] != "started":
            return "error", 0.0, None      # процесс не запустился

        start = time.perf_counter()
        if not recv.poll(TIME_LIMIT):
            return "timeout", float(TIME_LIMIT), None

        try:
            message = recv.recv()
        except EOFError:                   # процесс умер, не успев ответить
            return "error", time.perf_counter() - start, None
        if message[0] == "done":
            _, elapsed, moves = message
            return ("solved" if moves is not None else "no_solution"), elapsed, moves
        return "error", time.perf_counter() - start, None
    finally:
        if proc.is_alive():
            proc.terminate()
        proc.join()


def main():
    if not os.path.isdir(TRAINING_DIR):
        print(f"Папка не найдена: {TRAINING_DIR}")
        return
    files = sorted((f for f in os.listdir(TRAINING_DIR)
                    if f.lower().endswith(IMAGE_EXTENSIONS)), key=natural_key)
    if not files:
        print(f"В папке {TRAINING_DIR} нет картинок")
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_path = os.path.join(RESULTS_DIR, f"benchmark_{stamp}.csv")

    solved = 0
    total_time = 0.0
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["level", "time_seconds"])

        for n, file_name in enumerate(files, start=1):
            # название выводим сразу, результат допишем в эту же строку
            print(f"[{n}/{len(files)}] {file_name}: ", end="", flush=True)

            level = parse(os.path.join(TRAINING_DIR, file_name))
            issues = validate(level)
            if issues:
                print(f"пропущен ({issues[0].message})")
                continue

            status, seconds, moves = run_level(level)
            writer.writerow([file_name, round(seconds, 3)])
            f.flush()                      # результат не потеряется, если прервать прогон

            total_time += seconds
            if status == "solved":
                solved += 1
                print(f"решён за {seconds:.2f} с, ходов {moves}")
            elif status == "timeout":
                print(f"не решён за {TIME_LIMIT} с")
            elif status == "no_solution":
                print(f"решения нет ({seconds:.2f} с)")
            else:
                print("ошибка при решении")

    print("=" * 60)
    print(f"Решено {solved} из {len(files)}, суммарное время {total_time:.1f} с")
    print(f"Результаты: {csv_path}")


if __name__ == "__main__":
    main()