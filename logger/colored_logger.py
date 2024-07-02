#!/usr/bin/env python
# coding=utf-8

import logging
import os
from types import MethodType

from .formatter import ColoredFormatter, HTMLFormatter


def create_directory(filename: str):
    """
        Create a directory based on the path of the given file name.

        Args:
            filename (str): The name of the file.

        Returns:
            None
        """
    dirname = os.path.dirname(os.path.abspath(filename))
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


class ColoredLogger(logging.Logger):
    # Additional Level
    LOGGING_SYSTEM = 25  # Between INFO and WARNING
    LOGGING_NOTICE = 35  # Between WARNING and ERROR
    logging.addLevelName(LOGGING_SYSTEM, 'SYSTEM')
    logging.addLevelName(LOGGING_NOTICE, 'NOTICE')

    def __init__(self, name: str, level: int | str = logging.NOTSET):
        super().__init__(name, level=level)

    def system(self, message, *args, **kws):
        if self.isEnabledFor(ColoredLogger.LOGGING_SYSTEM):
            self._log(ColoredLogger.LOGGING_SYSTEM, message, args, **kws)

    def notice(self, message, *args, **kws):
        if self.isEnabledFor(ColoredLogger.LOGGING_NOTICE):
            self._log(ColoredLogger.LOGGING_NOTICE, message, args, **kws)

    @staticmethod
    def get_logger(
            name: str,
            module_name: str = None,
            console: bool = True,
            filename: str | None = None,
            html: str | None = None) -> logging.Logger:
        """
        Get a 'ColoredLogger' instance with configured handlers and formatters.

        This static method configures a logger with the specified name and level (DEBUG). It sets up three handlers:
        a console handler if 'console' is True, a file handler if 'filename' is provided, and an HTML file handler if
        'html' is provided. Each handler is configured with a 'ColoredFormatter' or 'HTMLFormatter' instance.

        Args:
            name (str): The name of the logger.
            module_name (str, optional): The name of the module, which will be included in the log records.
            console (bool, optional): Whether to enable the console handler. Default is True.
            filename (str, optional): The name of the log file. If specified, a file handler will be created.
            html (str, optional): The name of the HTML file. If specified, an HTML file handler will be created.

        Returns:
            logging.Logger: A configured 'ColoredLogger' instance.

        If the logger already exists when calling this method, it checks whether it is an instance of 'ColoredLogger'.
        If not, the 'ystem' and 'notice' methods will be bound to the existing logger object to ensure it has the
        extended functionality of these methods.
        """
        logging.setLoggerClass(ColoredLogger)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if not isinstance(logger, ColoredLogger):
            # 说明这个logger已经被取出来过，所以要做一下patch
            logger.system = MethodType(ColoredLogger.system, logger)
            logger.notice = MethodType(ColoredLogger.notice, logger)

        if len(logger.handlers) == 0:
            if console:
                ch = logging.StreamHandler()
                ch.setFormatter(ColoredFormatter(module_name=module_name))
                logger.addHandler(ch)

            if filename:
                create_directory(filename)
                fh = logging.FileHandler(filename)
                fh.setFormatter(ColoredFormatter(module_name=module_name))
                logger.addHandler(fh)

            if html:
                create_directory(html)
                hh = logging.FileHandler(html)
                hh.setFormatter(HTMLFormatter(module_name=module_name))
                logger.addHandler(hh)

        return logger


def get_logger(
        name: str,
        module_name: str = None,
        console: bool = True,
        filename: str | None = None,
        html: str | None = None) -> logging.Logger | ColoredLogger:
    return ColoredLogger.get_logger(
        name=name, module_name=module_name,
        console=console, filename=filename, html=html)
