#!/usr/bin/env python
# coding=utf-8

import logging
from types import MethodType

from .formatter import ColoredFormatter, HTMLFormatter


class CustomLogger(logging.Logger):
    # Additional Level
    LOGGING_SYSTEM = 25  # Between INFO and WARNING
    LOGGING_NOTICE = 35  # Between WARNING and ERROR
    logging.addLevelName(LOGGING_SYSTEM, 'SYSTEM')
    logging.addLevelName(LOGGING_NOTICE, 'NOTICE')

    def __init__(self, name: str, level: int | str = logging.NOTSET):
        super().__init__(name, level=level)

    def system(self, message, *args, **kws):
        if self.isEnabledFor(CustomLogger.LOGGING_SYSTEM):
            self._log(CustomLogger.LOGGING_SYSTEM, message, args, **kws)

    def notice(self, message, *args, **kws):
        if self.isEnabledFor(CustomLogger.LOGGING_NOTICE):
            self._log(CustomLogger.LOGGING_NOTICE, message, args, **kws)

    @staticmethod
    def get_logger(
            name: str,
            module_name: str = None,
            console: bool = True,
            filename: str | None = None,
            html: str | None = None) -> logging.Logger:
        logging.setLoggerClass(CustomLogger)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        if not isinstance(logger, CustomLogger):
            # 说明这个logger已经被取出来过，所以要做一下patch
            logger.system = MethodType(CustomLogger.system, logger)
            logger.notice = MethodType(CustomLogger.notice, logger)

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
        html: str | None = None) -> logging.Logger | CustomLogger:
    return CustomLogger.get_logger(
        name=name, module_name=module_name,
        console=console, filename=filename, html=html)
