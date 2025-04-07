"""
This module provides logging utilities for the JFrog Artifactory
 and Xray automation framework.

Purpose:
- To enable secure logging by masking sensitive information 
such as passwords and API keys.
- To provide reusable logging functions for capturing logs
 at different levels (info, warning, error, debug).
- To support logging to both console and files with consistent formatting.
- To handle exceptions and log them in a structured manner.
Author: Shwetha Kamath
"""

import logging
import os
import re
import sys
import time
import traceback

# This is non-exhaustive list of keywords for which values must be masked
RESERVED_KEYWORDS_FOR_MASKING = ["-p", "--password", "--apiKey", "--api_key", "--api-token"]


class SecureLogger(logging.Logger):
    """
    Class for secure logging.
    Contains function (mostly internal) to mask sensitive information
      and then print it
    Wrappers functions (external) on log info/warning/error/debug
    """

    def sensitive_info(self, msg, list_to_mask=None, *args, **kwargs):
        """
        Wrapper function to log information similar to log.info(),
        log.debug()
        Args:
            msg - Message to be printed
            list_to_mask - List of items to be masked
        """
        masked_msg = mask_text(msg, list_to_mask)
        super().info(masked_msg, *args, **kwargs)

    def sensitive_warning(self, msg, list_to_mask=None, *args, **kwargs):
        """
        Wrapper function to log information similar to log.warning()
        Args:
            msg - Message to be printed
            list_to_mask - List of items to be masked
        """
        masked_msg = mask_text(msg, list_to_mask)
        super().warning(masked_msg, *args, **kwargs)

    def sensitive_error(self, msg, list_to_mask=None, *args, **kwargs):
        """
        Wrapper function to log information similar to log.error()
        Args:
        msg - Message to be printed
        list_to_mask - List of items to be masked
        Returns:
            nothing
        """
        masked_msg = mask_text(msg, list_to_mask)
        super().error(masked_msg, *args, **kwargs)

    def sensitive_debug(self, msg, list_to_mask=None, *args, **kwargs):
        """
        Wrapper function to log information similar to log.debug()
        Args:
            msg - Message to be printed
            list_to_mask - List of items to be masked
        """
        masked_msg = mask_text(msg, list_to_mask)
        super().debug(masked_msg, *args, **kwargs)


def get_main_logger():
    """
    Get logger instance.

    return: Return the instance of logger.
    """
    # Set SecureLogger class for masking sensitive information
    logging.setLoggerClass(SecureLogger)
    # Get a logger instance
    return logging.getLogger(__name__)


def get_logging_formatter():
    """Ensure that all file and console logging has the same format."""
    logging.Formatter.converter = time.gmtime
    return logging.Formatter(
        "%(asctime)s Thrd:%(threadName)s: [%(module)s - %(funcName)s - %(lineno)d]: %(levelname)s %(message)s"
    )


def addStreamHandler(level):
    """Add a stdout handler (Python defaults to stderr.)."""

    # Create a new stream handler for stdout
    streamHandler = logging.StreamHandler(sys.stdout)

    # Set the logging level for the handler
    streamHandler.setLevel(level)

    # Get the logging formatter
    formatter = get_logging_formatter()

    # Set the formatter for the stream handler
    streamHandler.setFormatter(formatter)

    # Add the stream handler to the main logger
    get_main_logger().addHandler(streamHandler)


def add_file_handler(fileName: str, level: str):
    """
    Add FileHandler to hold the log based on log level.

    Returns the handler, which is needed if one wants to remove it later.

    :param fileName: Name of the log file
    :param level: Log level - DEBUG, INFO, WARNING, ERROR
    :return: The file handler object
    """
    logDir = os.path.dirname(fileName)

    # Create directory if it doesn't exist
    if not os.path.exists(logDir):
        os.mkdir(logDir)

    fileHandler = None

    try:
        # Using append mode to make sure full log has all the logs
        fileHandler = logging.FileHandler(fileName, "a")
        fileHandler.setLevel(level)
        formatter = get_logging_formatter()
        fileHandler.setFormatter(formatter)
        get_main_logger().addHandler(fileHandler)
    except Exception:
        pass
    return fileHandler


def log_exception(exType, exValue, exTb):
    """
    Python provides hooks (e.g. sys.excepthook) to catch exceptions in logs.

    We set up these hooks to use this function.
      If we don't, then exceptions
    will only be written to console, and a test suite's log won't show them.
    """
    # Format the exception traceback into a string
    lines = traceback.format_exception(exType, exValue, exTb)
    traceString = ""
    for line in lines:
        traceString += line

    # Log the exception traceback as an error
    get_main_logger().error(traceString)


def log_string_to_int(s):
    """Convert the given log level string, like "debug", to an int."""
    stringLevel = s.upper()
    return getattr(logging, stringLevel)


def set_up_logging(log_level, results_dir, file_handler):
    """
    Sets up log level and adds file handle for full.log.

    :param log_level: Log level - DEBUG, INFO, WARNING, ERROR
    :param results_dir: Result directory to store logs.
    :param file_handler: File handler
    """
    log = get_main_logger()
    # Set log level for the main logger
    log.setLevel(log_level)

    # Add console output for the entire run
    addStreamHandler(log_level)

    # Add file output for the entire run
    fullFile = os.path.join(results_dir, "full.log")
    add_file_handler(fullFile, log_level)

    # Set the exception hook for logging exceptions
    sys.excepthook = log_exception
    sys.unraisablehook = log_exception


def log_detailed(log, msg, component, sub_component, ltype="info"):
    """
    To log messages with component and sub-component.

    :param: log: Logging object
    :param: msg: Message to log
    :param: component: Component that is logging it
    :param: sub_component: Sub component that is logging the message
    :param: ltype: Log type ("info"/"error"/"debug")
    :return: None
    """
    if ltype == "info":
        log.info("{}->{}: {}".format(component, sub_component, msg))
    elif ltype == "error":
        log.error("{}->{}: {}".format(component, sub_component, msg))
    elif ltype == "debug":
        log.debug("{}->{}: {}".format(component, sub_component, msg))
    else:
        pass


def mask_text(message, list_to_mask=None):
    """
    Function to mask a text based on list of items to be masked or
      list of RESERVED_KEYWORDS_FOR_MASKING
    It masks all except last 4 characters of an item, and if size
      is <=4 mask all the characters.
    Args:
        message - Message to be printed
        list_to_mask (optional) - List of items to be masked.
        message - Original message with masked sensitive information
    """
    # If list of values to be masked not provided, check for the sensitive values in the text itself
    if not list_to_mask:
        list_to_mask = []
        for item in RESERVED_KEYWORDS_FOR_MASKING:
            # Do not remove the additional spacing
            match = re.search(item + " ", message, re.IGNORECASE)
            if match:
                pwd_to_mask = match.string[match.end() :]
                # Handle scenarios where a param doesn't even have a value
                # For e.g. --field1 --field2 val_2 --field3 --field4 val_4
                if not pwd_to_mask.startswith("--"):
                    list_to_mask.append(pwd_to_mask.split(" ")[0])

    # If the list is either provided as input or created as part of above step
    if list_to_mask:
        for item in list_to_mask:
            # Mask all characters
            masked_item = "".join(["*" for _ in item])

            message = message.replace(item, masked_item)
    return message
