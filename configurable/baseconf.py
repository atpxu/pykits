#!/usr/bin/env python
# coding=utf-8

from typing import Any

from pydantic import BaseModel


# TYPENAMES = {
#     'string': str,
#     'str': str,
#     'integer': int,
#     'int': int,
#     'float': float,
#     'double': float,
#     'boolean': bool,
#     'bool': bool
# }


class BaseConfig(BaseModel):
    """
    可配置参数基类，基于pydantic的BaseModel
    增加了set和get方法，用于设置和获取属性，便于动态的设置
    model_dump方法用于将配置转换为json dict，增加with_schema参数用于控制是否包含schema信息
    """

    def __init__(self, *args, **kwargs):
        if len(kwargs) > 0:
            # 如果有kwargs参数，使用kwargs参数初始化（保持和父类一致）
            super().__init__(**kwargs)
        else:
            # 如果没有kwargs参数，使用args参数初始化，其顺序和父类的Model_fields的keys保持顺序一致
            data = {k: v for k, v in zip(self.model_fields.keys(), args)}
            super().__init__(**data)

    def set(self, attr_name: str, attr_value: Any, allow_default: bool = True) -> bool:
        """
        设置属性值，如果类型不匹配，且allow_default为True，则使用默认值
        :param attr_name:
        :param attr_value:
        :param allow_default: 是否在设置失败的时候使用默认值
        :return: True if set successfully, False if set failed with default value used
        :raises: TypeError if set failed and allow_default is False; ValueError if attribute not found
        """
        # 检查属性是否存在
        if attr_name not in self.model_fields:
            raise ValueError(f"Attribute {attr_name} not found")

        # 获取该属性的类型
        field_info = self.model_fields[attr_name]
        # 尝试将值转换为相应的类型
        try:
            # 尝试使用类型直接转换值
            valid_value = field_info.annotation(attr_value)
            setattr(self, attr_name, valid_value)
            return True
        except (TypeError, ValueError) as e:  # 捕获常见的类型转换错误
            if allow_default and not field_info.is_required():
                setattr(self, attr_name, field_info.default)
                return False
            else:
                raise TypeError(f"Failed to convert {attr_value} to {field_info.annotation}: {e}")

    def get(self, attr_name: str) -> Any:
        """
        获取属性值
        :param attr_name:
        :return:
        """
        if attr_name not in self.model_fields:
            raise ValueError(f"Attribute {attr_name} not found")
        return getattr(self, attr_name)

    def model_dump(self, *args, with_schema: bool = False, **kwargs) -> dict:
        """
        将配置转换为dict，并根据参数决定是否包含schema信息
        :param args:
        :param with_schema:
        :param kwargs:
        :return:
        """
        dct = super().model_dump(*args, **kwargs)
        if not with_schema:
            return dct
        pdict = self.model_json_schema()['properties']
        for key, props in pdict.items():
            props['value'] = dct[key]
        return pdict
