"""
Utility module for defining custom exceptions used in tests or test helpers
"""


class TestRuntimeError(Exception):
    """Runtime exception during test case execution."""

    pass


class ResourceError(Exception):
    """Exception when file/resource not available in provided path/system."""

    pass
