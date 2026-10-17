import tkinter as tk

_root = None


def get_root():
    """Единственный скрытый корневой Tk() на всю программу."""
    global _root
    if _root is None:
        _root = tk.Tk()
        _root.withdraw()
    return _root

def bring_to_front(win):
    """Центрирует Toplevel, выводит поверх остальных окон и захватывает ввод.
    Окно создаётся из консольной программы и иначе может оказаться под другими окнами."""
    win.update_idletasks()
    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
    x = (win.winfo_screenwidth() - w) // 2
    y = (win.winfo_screenheight() - h) // 3
    win.geometry(f"+{x}+{y}")
    win.attributes("-topmost", True)
    win.after(200, lambda: win.attributes("-topmost", False))
    win.focus_force()
    win.grab_set()
    
def set_root(root):
    """Регистрирует главное окно как корневое: окна, которые берут get_root(),
    будут открываться поверх него. Вызывать до первого get_root()."""
    global _root
    if _root is not None and _root is not root:
        raise RuntimeError("Корневое окно уже создано")
    _root = root