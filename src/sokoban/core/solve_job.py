"""Решение уровня в отдельном процессе: интерфейс не зависает, поиск можно отменить."""
import multiprocessing as mp
import signal
import time

from core.solver import solve

RUNNING = "running"
SOLVED = "solved"
NO_SOLUTION = "no_solution"
CANCELLED = "cancelled"
ERROR = "error"


def _worker(level, conn):
    # Ctrl+C в терминале, из которого запущена программа, не должен ломать поиск: процесс завершает родитель    # Ctrl+C в консоли отменяет родитель; поиск сам по себе прерывать не должен
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        start = time.perf_counter()
        path = solve(level)
        conn.send(("done", time.perf_counter() - start, path))
    except BaseException as e:               # например MemoryError
        conn.send(("error", repr(e)))
    finally:
        conn.close()


class SolveJob:
    """Запущенный поиск решения.
    После создания процесс уже работает. Окно периодически вызывает poll(),
    а кнопка «Отмена» вызывает cancel().

    status: RUNNING, SOLVED, NO_SOLUTION, CANCELLED или ERROR
    path: список ходов (если SOLVED)
    solver_time: секунды работы самого солвера, без запуска процесса (если SOLVED или NO_SOLUTION)
    error: текст ошибки (если ERROR)
    elapsed: секунды с запуска; идёт, пока поиск работает, и замирает после его конца."""

    def __init__(self, level):
        self.status = RUNNING
        self.path = None
        self.solver_time = None
        self.error = None
        self._started = time.perf_counter()
        self._finished = None
        self._recv, send = mp.Pipe(duplex=False)
        self._proc = mp.Process(target=_worker, args=(level, send), daemon=True)
        self._proc.start()
        send.close()                         # в родителе конец для записи не нужен

    @property
    def elapsed(self):
        end = self._finished if self._finished is not None else time.perf_counter()
        return end - self._started

    def poll(self):
        """Проверяет, не закончился ли поиск. Возвращает True, если он завершён (любым исходом)."""
        if self.status != RUNNING:
            return True
        if self._recv.poll():
            self._read()
        elif not self._proc.is_alive():
            if self._recv.poll():            # результат мог прийти прямо перед завершением процесса
                self._read()
            else:
                self._finish(ERROR, "Процесс решения завершился неожиданно "
                                    "(возможно, не хватило памяти)")
        return self.status != RUNNING

    def cancel(self):
        """Останавливает поиск. Можно вызывать повторно и после завершения."""
        if self.status == RUNNING:
            self._finish(CANCELLED)

    def _read(self):
        try:
            message = self._recv.recv()
        except (EOFError, OSError):
            self._finish(ERROR, "Процесс решения завершился неожиданно")
            return
        if message[0] == "done":
            _, self.solver_time, self.path = message
            self._finish(SOLVED if self.path is not None else NO_SOLUTION)
        else:
            self._finish(ERROR, message[1])

    def _finish(self, status, error=None):
        self.status = status
        self.error = error
        self._finished = time.perf_counter()
        if self._proc.is_alive():
            self._proc.terminate()
        self._proc.join(timeout=2)
        self._recv.close()