#!/usr/bin/env python
# coding=utf-8
class NullLogger:
    """Do nothing logger"""

    def log(self, message, *args, **kwargs):
        """
        Log a message, ignoring all other params like *, ** for extra params.

        Parameters message: The message to log.
        """
        pass  # do nothing

    # Alias all other logging methods to log to maintain compatibility API
    critical = error = exception = warning = info = debug = log

    # Alias system and notice methods to log
    system = notice = log



null_logger = NullLogger()


class PrintLogger:
    """
    A simple logging class that redirects all log messages to the standard output.
    """

    def log(self, message, *args, **kwargs):
        """
        Log a message to stdout.

        Args:
            message (str): The message to be logged.
            *args: Optional positional arguments to include in the log message.
            **kwargs: Optional keyword arguments to include in the log message.

        Returns:
            None
        """
        print(message)  # just print

    # Alias critical messages as log messages
    critical = error = exception = warning = info = debug = log

    # Alias system and notice messages as log messages
    system = notice = log


print_logger = PrintLogger()
