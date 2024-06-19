import operator
from typing import Any, Callable

opfunc_names = {
    func: name
    for name, func in vars(operator).items()
    if callable(func) and not name.startswith('__')}

opname_funcs = {
    name: func
    for name, func in vars(operator).items()
    if callable(func) and not name.startswith('__')}


class Condition:
    def __init__(self, name: str, val: Any = None, func: Callable = operator.eq, val2: Any = None):
        """

        :param name: the key of storage to get
        :param val: default value of the key
        :param func: the function to compare, should be operator.eq/lt/gt/is/...
        :param val2: the value to compare
        """
        self.name = name
        self.default_value = val
        self.func = func  # operator.eq/lt/gt/is/...
        self.target_value = val2

    def satisfy(self, storage):
        """
        :param storage: a dict like object support get function to retrieve the value by a key
        :return: True/False
        """
        val1 = storage.get(self.name, self.default_value)
        return self.func(val1, self.target_value)

    def dump(self):
        return {
            'name': self.name,
            'val': self.default_value,
            'func': self.func.__name__,
            'val2': self.target_value
        }

    @staticmethod
    def load(cond: dict):
        if 'func' in cond and isinstance(cond['func'], str):
            try:
                cond['func'] = globals()[cond['func']]
            except KeyError:
                cond['func'] = opname_funcs[cond['func']]
        return Condition(
            name=cond['name'],
            val=cond.get('val'),
            func=cond.get('func', operator.eq),
            val2=cond.get('val2')
        )
