"""
Module consists of custom Exceptions for Jfrog related tests and helpers
# Author: Shwetha Kamath
"""


class DockerImagePullError(Exception):
    """
    Class to propagate errors related to the docker pull image command.
    """

    pass


class DockerLoginError(Exception):
    """
    Class to propagate errors related to the docker login.
    """

    pass


class DockerPushError(Exception):
    """
    Class to propagate errors related to the docker push.
    """

    pass


class JfrogAPIError(Exception):
    """Class to propagate any errors or unexpected status code in
    the response of an API Call."""

    pass


class JfrogAuthenticationError(Exception):
    """Class to propagate errors related to logging into fetching API
    token for Jfrog service."""

    pass


class FileNotFoundError(Exception):
    """Class to propagate errors related to File related operations."""

    pass
