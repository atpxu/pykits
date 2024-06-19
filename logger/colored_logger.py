#!/usr/bin/env python
# coding=utf-8

import logging
from types import MethodType

from .formatter import ColoredFormatter, HTMLFormatter


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
                fh = logging.FileHandler(filename)
                fh.setFormatter(ColoredFormatter(module_name=module_name))
                logger.addHandler(fh)

            if html:
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
