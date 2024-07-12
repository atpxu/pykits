import threading


def singleton(cls):
    """
    A decorator to make a class a Singleton
    :param cls: The class to be made a thread safe Singleton
    """

    __inst = {}
    __lock = threading.Lock()

    def _get_inst(*args, **kwargs):
        if cls in __inst:
            return __inst[cls]
        with __lock:
            if cls not in __inst:
                __inst[cls] = cls(*args, **kwargs)
        return __inst[cls]

    return _get_inst
