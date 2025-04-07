"""
This module defines enumerations
 for Jfrog API models

Author: Shwetha Kamath
"""

from enum import Enum


class HttpRequestType(Enum):
    """
    Enumeration for HTTP request methods.

    This enum defines the standard HTTP methods used for making API requests.

    Attributes:
        PUT (str): Represents the HTTP PUT method.
        GET (str): Represents the HTTP GET method.
        POST (str): Represents the HTTP POST method.
        DELETE (str): Represents the HTTP DELETE method.
    """

    PUT = "PUT"
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class JfrogEndpoints(Enum):
    """
    Enumeration for JFrog API endpoints.

    This enum defines the base URL and endpoint paths for
      interacting with JFrog Artifactory APIs.

    Attributes:
        JFROG_BASE_URL (str): The base URL for the JFrog instance.
        CREATE_OR_FETCH_REPO (str): Endpoint for creating or fetching a
          repository.
        CREATE_SECURITY_POLICY (str): Endpoint for creating security
          policies in JFrog Xray.
        CREATE_WATCH (str): Endpoint for creating watches in JFrog Xray.
        GET_SCAN_STATUS (str): Endpoint for retrieving the scan
          status of an artifact.
        GET_VIOLATIONS (str): Endpoint for retrieving violations
          for scanned artifacts.
    """

    JFROG_BASE_URL = "https://trialxylzua.jfrog.io"
    CREATE_OR_FETCH_REPO = "/artifactory/api/repositories/{}"
    CREATE_SECURITY_POLICY = "/xray/api/v2/policies"
    CREATE_WATCH = "/xray/api/v2/watches"
    GET_SCAN_STATUS = "/xray/api/v1/artifact/status"
    GET_VIOLATIONS = "/xray/api/v1/violations"
