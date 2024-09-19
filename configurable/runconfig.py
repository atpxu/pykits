from abc import ABC

from .configurable import Configurable
from .runnable import Runnable


class RunnableConfigurable(Configurable, Runnable, ABC):
    pass
