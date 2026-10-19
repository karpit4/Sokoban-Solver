import tkinter as tk
from tkinter import messagebox

from core.playback import SolutionPlayback
from core.rules import DIRECTIONS
from core.session import GameSession
from core.state import symbol_at
from gui.app import bring_to_front, get_root
from gui.board_view import BoardView
from gui.styling import Styler
from gui.settings import open_settings
from gui.theme import ThemeManager

# Стрелки приходят как keysym ("Up", "Down", "Left", "Right": те же имена, что в DIRECTIONS).
# Буквы определяются по коду клавиши, чтобы работали в любой раскладке (коды Windows).
WASD_KEYCODES = {87: "Up", 65: "Left", 83: "Down", 68: "Right"}   # W, A, S, D
UNDO_KEYCODE = 90      # Z
RESTART_KEYCODE = 82   # R

SPEEDS = [500, 250, 120, 60, 25]   # пауза между ходами при показе решения, мс
DEFAULT_SPEED = 2                  # индекс в SPEEDS
START_DELAY = 500                  # пауза перед первым ходом показа, мс

HINT = "Стрелки/WASD: ход    Клик: перейти    Z: отмена    R: заново"
REPLAY_HINT = "Стрелки/WASD: ход    Клик: перейти    Z: отмена    R: повторить показ"
PLAYING_HINT = "Идёт показ решения: ходы выполняются автоматически"


class GameFrame(tk.Frame):
    """Окно игры в виде Frame: его можно поместить и в отдельное окно (play_level),
    и позже в главное окно программы.
    on_exit(won, moves) вызывается, когда игрок нажал «Выйти»:
    won - пройден ли уровень, moves - сделанные ходы.
    solution: список ходов солвера. Если он задан, решение проигрывается автоматически
    (ходы применяются напрямую, фокус окна для этого не нужен), а кнопка «Заново»
    превращается в «Повторить показ» и всегда проигрывает решение снова."""

    def __init__(self, master, matrix, name, themes, on_exit, solution=None, on_settings = None):
        super().__init__(master, padx=12, pady=12)
        self.themes = themes
        self.theme = themes.theme
        self.on_exit = on_exit
        self.session = GameSession(matrix)
        self._solution = list(solution) if solution else None     # нужен для повторного показа
        self.playback = SolutionPlayback(self.session, self._solution) if solution else None
        self._playing = self.playback is not None
        self._paused = False
        self._timer = None             # id отложенного шага показа
        self._speed = DEFAULT_SPEED
        self.styler = Styler()
        self.styler.add(self, "bg")

        self._label(self, text=name, font=("Segoe UI", 12, "bold")).pack(pady=(0, 8))

        self.board = BoardView(self, self.theme)
        self.board.pack()
        self.board.set_matrix(matrix)

        self.status_label = self._label(self, font=("Segoe UI", 11, "bold"))
        self.status_label.pack(pady=(8, 0))
        self.hint_label = self._label(self, font=("Segoe UI", 9))
        self.hint_label.pack(pady=(2, 8))

        if self._playing:
            self._build_playback_row()

        buttons = self._frame(self)
        buttons.pack()
        self._buttons = buttons        # строка показа возвращается именно перед ней
        self.undo_btn = self._button(buttons, "Отменить (Z)", self._undo)
        if self._solution is not None:
            # с решением эта кнопка всегда проигрывает его заново, а не возвращает к началу
            self.restart_btn = self._button(buttons, "Повторить показ (R)", self._restart, width=19)
        else:
            self.restart_btn = self._button(buttons, "Заново (R)", self._restart)
        settings_btn = self._button(buttons, "Настройки", on_settings) if on_settings else None
        self.exit_btn = self._button(buttons, "Выйти", self.close)
        for btn in (self.undo_btn, self.restart_btn, settings_btn, self.exit_btn):
            if btn is not None:
                btn.pack(side="left", padx=4)

        self.styler.apply(self.theme)
        self.themes.subscribe(self, self._on_theme_change)

        # Клавиши ловит сам Frame, поэтому после каждого нажатия кнопки фокус возвращается ему
        self.bind("<Key>", self._on_key)
        self.bind("<Destroy>", self._on_destroy, add="+")   # add="+": иначе пропадёт отписка от темы
        self.board.canvas.bind("<Button-1>", self._on_click)
        self._update_status()

        if self._playing:
            self._schedule(START_DELAY)

    # ---------- оформление ----------

    def _frame(self, parent):
        return self.styler.add(tk.Frame(parent), "bg")

    def _label(self, parent, **options):
        return self.styler.add(tk.Label(parent, **options), "label")

    def _button(self, parent, text, command, width=14):
        def run():
            command()
            if self.winfo_exists():      # «Выйти» уже закрыло окно
                self.focus_set()
        btn = tk.Button(parent, text=text, command=run, width=width, relief="flat", pady=4)
        return self.styler.add(btn, "button")

    def _on_theme_change(self, theme):
        self.theme = theme
        self.styler.apply(theme)
        self.board.set_theme(theme)  # перерисовывает текущее положение, а не начальное
        self._update_status()

    # ---------- показ решения ----------

    def _build_playback_row(self):
        self.playback_row = self._frame(self)
        self.playback_row.pack(pady=(0, 8))
        self.pause_btn = self._button(self.playback_row, "Пауза", self._toggle_pause, width=12)
        self.take_btn = self._button(self.playback_row, "Взять управление", self._end_playback, width=16)
        self.slower_btn = self._button(self.playback_row, "−", lambda: self._change_speed(-1), width=3)
        self.speed_label = self._label(self.playback_row, width=14)
        self.faster_btn = self._button(self.playback_row, "+", lambda: self._change_speed(1), width=3)
        for widget in (self.pause_btn, self.take_btn, self.slower_btn,
                       self.speed_label, self.faster_btn):
            widget.pack(side="left", padx=3)
        self._update_speed_label()

    def _update_speed_label(self):
        self.speed_label.config(text=f"Скорость: {self._speed + 1}/{len(SPEEDS)}")

    def _change_speed(self, step):
        self._speed = min(max(self._speed + step, 0), len(SPEEDS) - 1)
        self._update_speed_label()     # новая скорость действует со следующего хода

    def _schedule(self, delay):
        self._cancel_timer()
        self._timer = self.after(delay, self._play_step)

    def _cancel_timer(self):
        if self._timer is not None:
            self.after_cancel(self._timer)
            self._timer = None

    def _play_step(self):
        self._timer = None
        if not self._playing or self._paused:
            return
        self._apply(self.playback.step())
        if self.playback.finished:
            self._end_playback()
        else:
            self._schedule(SPEEDS[self._speed])

    def _toggle_pause(self):
        if self._paused:
            self._paused = False
            self.pause_btn.config(text="Пауза")
            self._schedule(SPEEDS[self._speed])
        else:
            self._paused = True
            self._cancel_timer()
            self.pause_btn.config(text="Продолжить")

    def _end_playback(self):
        """Показ закончился или игрок взял управление: дальше обычная игра с текущего места."""
        self._cancel_timer()
        self._playing = False
        self._paused = False
        self.playback_row.pack_forget()
        self._update_status()

    def _start_playback(self):
        """Запускает показ решения с начала (скорость остаётся выбранной)."""
        self.playback = SolutionPlayback(self.session, self._solution)
        self._playing = True
        self._paused = False
        self.pause_btn.config(text="Пауза")
        self.playback_row.pack(pady=(0, 8), before=self._buttons)   # на прежнее место, над кнопками
        self._update_status()
        self._schedule(START_DELAY)

    def _on_destroy(self, event):
        # отложенный шаг не должен сработать после закрытия окна
        if event.widget is self:
            self._cancel_timer()

    # ---------- игра ----------

    def _apply(self, cells):
        """Перерисовывает только изменившиеся клетки и обновляет строку состояния."""
        state = self.session.state
        for i, j in cells:
            self.board.set_cell(i, j, symbol_at(state, (i, j)))
        self._update_status()

    def _update_status(self):
        n = self.session.move_count
        if self._playing:
            text = f"Показ решения: {self.playback.index} из {self.playback.total}"
        elif self.session.is_won:
            text = f"Уровень пройден! Ходов: {n}"
        else:
            text = f"Ходов: {n}"
        self.status_label.config(text=text)
        if self._playing:
            hint = PLAYING_HINT
        else:
            hint = HINT if self._solution is None else REPLAY_HINT
        self.hint_label.config(text=hint)
        # во время показа отмена и перезапуск недоступны: они сбили бы решение
        can_undo = self.session.can_undo and not self._playing
        # повторить показ можно в любой момент после его конца или после «Взять управление»,
        # даже из начальной позиции; обычное «Заново» нужно, только если есть что сбрасывать
        can_restart = (not self._playing) if self._solution is not None else can_undo
        self.undo_btn.config(state="normal" if can_undo else "disabled")
        self.restart_btn.config(state="normal" if can_restart else "disabled")

    def _on_key(self, event):
        if self._playing:
            return
        direction = event.keysym if event.keysym in DIRECTIONS else WASD_KEYCODES.get(event.keycode)
        if direction:
            self._apply(self.session.move(direction))
        elif event.keycode == UNDO_KEYCODE:
            self._undo()
        elif event.keycode == RESTART_KEYCODE:
            self._restart()

    def _on_click(self, event):
        """Клик по клетке: игрок идёт туда, если дойти можно, не двигая коробки."""
        self.focus_set()
        if self._playing:
            return
        cell = self.board.cell_at(event.x, event.y)
        if cell is not None:
            self._apply(self.session.walk_to(cell))

    def _undo(self):
        self._apply(self.session.undo())

    def _restart(self):
        """Без решения: уровень с начала. С решением: показ решения заново."""
        replay = self._solution is not None
        if self.session.can_undo and not self.session.is_won:
            question = ("Показать решение заново? Текущие ходы будут потеряны." if replay
                        else "Начать уровень сначала? Ходы будут потеряны.")
            if not messagebox.askyesno("Заново", question, parent=self):
                self.focus_set()
                return
        self._apply(self.session.restart())
        if replay:
            self._start_playback()

    def close(self):
        self.on_exit(self.session.is_won, self.session.moves)


def play_level(matrix, name="", parent=None, themes=None, solution=None):
    """Открывает окно игры и ждёт, пока игрок его закроет.
    solution: список ходов солвера для автоматического показа (необязательно).
    Возвращает (won, moves): пройден ли уровень и список сделанных ходов."""
    get_root()                     # корень должен существовать до создания окна
    if themes is None:
        themes = ThemeManager()

    win = tk.Toplevel(get_root() if parent is None else parent)
    if parent is not None:
        win.transient(parent)
    win.title("Игра")
    win.resizable(False, False)

    result = {"won": False, "moves": []}

    def finish(won, moves):
        result["won"], result["moves"] = won, moves
        win.destroy()

    frame = GameFrame(win, matrix, name, themes, finish, solution,
                      on_settings=lambda: open_settings(themes, win))
    frame.pack()
    win.protocol("WM_DELETE_WINDOW", frame.close)
    bring_to_front(win)
    frame.focus_set()              # после focus_force окна: клавиши идут во Frame
    win.wait_window()
    get_root().update()            # окно должно исчезнуть до следующих действий
    return result["won"], result["moves"]