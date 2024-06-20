#!/usr/bin/env python
# coding=utf-8
class NullLogger:
    """Do nothing logger"""
    def log(self, message, *args, **kwargs):
        pass  # do nothing

    critical = error = exception = warning = info = debug = log

    system = notice = log


null_logger = NullLogger()
