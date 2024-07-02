#!/usr/bin/env python
# coding=utf-8
import asyncio
import logging
import os.path
import threading


# 基础配置
class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter that adds color to log level names.

    Attributes:
        COLORS (dict): A dictionary mapping log level names to ANSI escape codes for colors.
    """

    COLORS = {
        'DEBUG': '\033[0m',  # Default color
        'INFO': '\033[0m',  # Default color
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m',  # Red
        'SYSTEM': '\033[92m',  # Green
        'NOTICE': '\033[36m',  # Cyan
        'RESET': '\033[0m'  # Reset color
    }

    def __init__(self, module_name=None, *args, **kwargs):
        """
        Initialize the ColoredFormatter instance.

        Args:
            module_name (str, optional): The name of the module or component the logger is associated with.
            *args: Additional positional arguments passed to the superclass constructor.
            **kwargs: Additional keyword arguments passed to the superclass constructor.
        """
        super().__init__(*args, **kwargs)
        self.module_name = module_name

    def colored_level(self, levelname):
        """
        Get the colored representation of the log level name.

        Args:
            levelname (str): The name of the log level.

        Returns:
            str: The colored log level name.
        """
        return f'{ColoredFormatter.COLORS.get(levelname, self.COLORS["RESET"])}' \
               f'[{levelname}]' \
               f'{ColoredFormatter.COLORS["RESET"]}'

    def format(self, record):
        """
        Format the log record into a string representation.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record.
        """
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
    """
    A custom logging formatter that inherits from ColoredFormatter.
    It provides formatting for log records in HTML format, specifically for coloring the level names of log records.

    COLORS: A dictionary that defines the colors for different log levels.
    colored_level: This method colors the log level name based on the color defined in the COLORS dictionary.
    format: This method formats the log record and adds <br> after the formatted string.
    """
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
        """
        Coloring the log level name based on the color defined in the COLORS dictionary.

        Parameters:
            levelname (str): The name of the log level to be colored.

        Returns:
            str: The colored level name.
        """
        color = HTMLFormatter.COLORS.get(levelname, 'black')
        return f'<span style="color: {color}">{levelname}</span>'

    def format(self, record):
        """
        Formats the log record sent to the formatter and adds <br> to the end of the record to ensure it is displayed correctly in HTML format.

        Parameters:
            record (LogRecord): The log record to be formatted.

        Returns:
            str: The formatted log record as an HTML string.
        """
        msg = super().format(record)
        return msg + '<br>'

