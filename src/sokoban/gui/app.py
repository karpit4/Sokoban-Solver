import tkinter as tk

_root = None


def get_root():
    """Единственный скрытый корневой Tk() на всю программу."""
    global _root
    if _root is None:
        _root = tk.Tk()
        _root.withdraw()
    return _root