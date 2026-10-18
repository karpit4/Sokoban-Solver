import threading

from core.solve_job import CANCELLED, NO_SOLUTION, SOLVED, SolveJob
from gui.board_view import BoardView
from gui.screens.base import Screen
from gui.screens.game import GameScreen
from tools.runner import execute_solution

POLL_MS = 100          # как часто проверяется, закончился ли поиск
TYPING_POLL_MS = 200   # как часто проверяется, закончился ли ввод через pyautogui


class SolveScreen(Screen):
    """Решение уровней по очереди: живой счётчик времени, кнопка «Отмена», затем результат.
    levels: список (название, матрица). back() вызывается, когда работа закончена.
    index и job нужны, чтобы вернуться на экран после показа решения в игре:
    с готовым job поиск заново не запускается."""

    def __init__(self, master, app, levels, back, index=0, job=None):
        super().__init__(master, app)
        self.levels = levels
        self.back = back
        self.index = index
        self.job = None
        self._timer = None
        self._typing = None            # поток ввода решения через pyautogui
        self.configure(padx=24, pady=20)

        self.title_label = self.label(self, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(pady=(0, 8))
        self.board = BoardView(self, app.themes.theme)
        self.board.pack()
        self.status_label = self.label(self, font=("Segoe UI", 11, "bold"))
        self.status_label.pack(pady=(10, 0))
        self.detail_label = self.label(self, font=("Segoe UI", 10), wraplength=520)
        self.detail_label.pack(pady=(2, 10))

        # кнопки действий создаются один раз и переключаются: Styler хранит виджеты навсегда
        self.actions = self.frame(self)
        self.actions.pack()
        self._btns = [self.button(self.actions, "", lambda: None, width=22) for _ in range(4)]

        self.bind("<Destroy>", self._on_destroy, add="+")   # add="+": иначе пропадёт отписка от темы
        self._show_level(job)

    def on_theme_change(self, theme):
        self.board.set_theme(theme)

    # ---------- кнопки действий ----------

    def _set_actions(self, items):
        """items: список (текст, команда). Остальные кнопки скрываются."""
        for btn in self._btns:
            btn.pack_forget()
        for btn, (text, command) in zip(self._btns, items):
            btn.config(text=text, command=command)
            btn.pack(side="left", padx=4)

    # ---------- поиск ----------

    def _show_level(self, job=None):
        name, matrix = self.levels[self.index]
        self.title_label.config(text=f"Уровень {self.index + 1} из {len(self.levels)}: {name}")
        self.board.set_matrix(matrix)
        if job is not None:            # возврат из игры: результат уже есть
            self.job = job
            self._show_result()
            return
        self.job = SolveJob(matrix)
        self.status_label.config(text="Идёт поиск решения...")
        self.detail_label.config(text="Прошло: 0.0 с")
        self._set_actions([("Отмена", self._cancel)])
        self._schedule_tick()

    def _schedule_tick(self):
        self._timer = self.after(POLL_MS, self._tick)

    def _tick(self):
        self._timer = None
        if self.job.poll():
            self._show_result()
        else:
            self.detail_label.config(text=f"Прошло: {self.job.elapsed:.1f} с")
            self._schedule_tick()

    def _cancel(self):
        self._cancel_timer()
        self.job.cancel()
        self._show_result()

    def _cancel_timer(self):
        if self._timer is not None:
            self.after_cancel(self._timer)
            self._timer = None

    def _on_destroy(self, event):
        # уход с экрана не должен оставлять поиск работать в фоне
        if event.widget is self:
            self._cancel_timer()
            if self.job is not None:
                self.job.cancel()

    # ---------- результат ----------

    def _show_result(self):
        job = self.job
        last = self.index == len(self.levels) - 1
        items = []
        if job.status == SOLVED:
            self.status_label.config(text=f"Решение найдено. Ходов: {len(job.path)}")
            self.detail_label.config(text=f"Время поиска: {job.solver_time:.2f} с")
            items += [("Показать в игре", self._show_in_game),
                      ("Ввести через pyautogui", self._type_solution)]
        elif job.status == NO_SOLUTION:
            self.status_label.config(text="Решений не найдено")
            self.detail_label.config(text=f"Время поиска: {job.solver_time:.2f} с")
        elif job.status == CANCELLED:
            self.status_label.config(text="Поиск отменён")
            self.detail_label.config(text=f"Прошло: {job.elapsed:.1f} с")
        else:
            self.status_label.config(text="Ошибка при решении")
            self.detail_label.config(text=job.error or "")
        if last:
            items.append(("Готово", self.back))
        else:
            items += [("Следующий уровень", self._next), ("Закончить", self.back)]
        self._set_actions(items)

    def _next(self):
        self.index += 1
        self._show_level()

    def _show_in_game(self):
        name, matrix = self.levels[self.index]
        levels, back, index, job = self.levels, self.back, self.index, self.job
        self.app.show(GameScreen, matrix, f"{name}: решение солвера",
                      back=lambda: self.app.show(SolveScreen, levels, back, index, job),
                      solution=job.path)

    # ---------- ввод через pyautogui ----------

    def _type_solution(self):
        """Ввод идёт в отдельном потоке, чтобы окно не зависало: runner ждёт 5 секунд
        (за это время нужно переключиться на окно игры) и нажимает клавиши."""
        self.status_label.config(text="Ввод решения через pyautogui")
        self.detail_label.config(
            text="Через 5 секунд программа нажмёт клавиши в активном окне: "
                 "переключитесь на окно игры")
        self._set_actions([])
        self._typing = threading.Thread(target=execute_solution, args=(self.job.path,), daemon=True)
        self._typing.start()
        self._timer = self.after(TYPING_POLL_MS, self._poll_typing)

    def _poll_typing(self):
        self._timer = None
        if self._typing.is_alive():
            self._timer = self.after(TYPING_POLL_MS, self._poll_typing)
        else:
            self._typing = None
            self._show_result()