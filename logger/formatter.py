#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import os.path
import threading


# 基础配置
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[0m',  # 默认颜色
        'INFO': '\033[0m',  # 默认颜色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[91m',  # 红色
        'SYSTEM': '\033[92m',  # 绿色
        'NOTICE': '\033[36m',  # 深青色
        'RESET': '\033[0m'  # 重置
    }

    def __init__(self, module_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module_name = module_name

    def colored_level(self, levelname):
        return f'{ColoredFormatter.COLORS.get(levelname, self.COLORS["RESET"])}' \
               f'[{levelname}]' \
               f'{ColoredFormatter.COLORS["RESET"]}'

    def format(self, record):
        level_name = record.levelname
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)

        # for tid
        try:
            task = asyncio.current_task()
            if task is None:
                task_info = f't-{threading.current_thread().ident}'
            else:
                task_info = f'a-{id(task)}'
        except RuntimeError:
            task_info = f't-{threading.current_thread().ident}'

        filename = self.module_name if self.module_name else record.filename
        fn, _ = os.path.splitext(filename)

        msg = f'[{record.asctime}]' \
              f'{self.colored_level(level_name)}' \
              f'[{record.process}]' \
              f'[{task_info}]' \
              f'[{fn}]' \
              f'  {record.message}'
        return msg


class HTMLFormatter(ColoredFormatter):
    COLORS = {
        'DEBUG': 'black',
        'INFO': 'black',
        'WARNING': 'orange',
        'ERROR': 'red',
        'CRITICAL': 'red',
        'SYSTEM': 'green',
        'NOTICE': 'darkcyan'
    }

    def colored_level(self, levelname):
        color = HTMLFormatter.COLORS.get(levelname, 'black')
        return f'<span style="color: {color}">{levelname}</span>'

    def format(self, record):
        msg = super().format(record)
        return msg + '<br>'
