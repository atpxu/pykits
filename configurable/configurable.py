#!/usr/bin/env python
# coding=utf-8

import json
from abc import ABC
from typing import Any

from .baseconf import BaseConfig


class Configurable(ABC):
    """
    可配置的抽象类，继承该类的类可以通过configs属性设置和获取配置
    默认包括两个属性：name和description，用于基本的描述信息

    """
    name: str = 'Configurable',
    description: str = 'Configurable抽象类'

    configs: BaseConfig = None
    """可配置参数列表"""

    def set(self, key: str, value: Any, allow_default: bool = True):
        """
        改配置，必须是configs中存在的字段才允许修改

        :param self:
        :param key:
        :param value:
        :param allow_default: 类型不匹配的时候是否设置为默认值
            True，设置成功
            False，如果类型不匹配，无论是否采用了默认值，都算修改失败
        :return: 是否设置成功（但不一定发生变化）
        """
        try:
            return self.configs.set(key, value, allow_default)
        except (TypeError, ValueError):
            return False

    def get(self, key: str, default: Any = None):
        """
        获取配置

        :param key:
        :param default:
        :return:
        """
        if key not in self.configs.model_fields:
            return default
        return self.configs.get(key)

    def dump(self, with_schema=True) -> dict:
        """
        dump to dict, with schema or not
        :param with_schema:
        :return:
        """
        obj = {
            'class': self.__class__.__name__,
            'name': self.name,
            'description': self.description,
            'configs': self.configs.model_dump(with_schema=with_schema)}
        return obj

    def load(self, data: dict):
        """
        load from dict
        :param data:
        :return:
        """
        self.name = data['name']
        self.description = data['description']
        cfgs = data['configs']
        self.configs = self.configs.model_copy(update=cfgs)

    def json(
            self, with_schema: bool = True,
            skip_keys: bool = False, ensure_ascii: bool = False,
            check_circular: bool = True, sort_keys: bool = False,
            allow_nan: bool = True, indent: int | str | None = None,
            separators: tuple[str, str] | None = None) -> str:
        """dump to json"""
        return json.dumps(
            self.dump(with_schema=with_schema),
            skipkeys=skip_keys, ensure_ascii=ensure_ascii,
            indent=indent, check_circular=check_circular,
            sort_keys=sort_keys, allow_nan=allow_nan, separators=separators)
