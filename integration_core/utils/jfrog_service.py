"""
This module provides the 'JFrogAPIClient' class to interact with
 JFrog Artifactory and Xray APIs.

Purpose:
- To simplify interactions with JFrog services such as repository
 management, security policy creation, watch creation, artifact scanning,
   and violation retrieval.

Note:
- Ensure that the 'requests' and 'retry' Python packages are
 installed in the environment.
- The base URL for JFrog should be configured correctly, 
and valid credentials or an API token must be provided.

Author: Shwetha Kamath
"""

from datetime import datetime

import requests
from retry import retry

from integration_core import enums, exceptions
from util import logging

log = logging.get_main_logger()


class JFrogAPIClient:
    """
    This class represents JfrogAPIClient class to interact with
    Jfrog Apis
    """

    def __init__(self, base_url, auth_token=None, username=None, password=None):
        """
        Initialize an instance of the JFrogAPIClient class.

        Args:
        base_url (str): The base URL of the JFrog Artifactory
        auth_token (str, optional): The API token for authentication.
        Defaults to None.
        username (str): The username for basic authentication.
        password (str): The password for basic authentication
        """
        log.debug("Initializing JFrogAPIClient instance.")
        self.base_url = base_url
        self._token = None
        self.headers = {
            "Authorization": f"Bearer {self._token}" if auth_token else None,
            "Content-Type": "application/json",
        }
        self.username = username
        self.password = password

    @retry(exceptions.JfrogAPIError, tries=3, delay=10)
    def _make_request(
        self, request_type, service_endpoint, proxies=None, data=None, params=None, headers=None
    ):
        """
        Make an HTTP request to the JFrog API.

        This method handles the construction and execution of HTTP requests
          to the JFrog API.
        It retries the request up to 3 times in case of transient failures,
          with a delay of 10 seconds between retries

        Args:
        request_type (enums.HttpRequestType): The HTTP request type (e.g., GET, POST, PUT).
        service_endpoint (str): The API endpoint to which the request is made (relative to the base URL).
        proxies (dict, optional): Proxy configuration for the request. Defaults to None.
        data (dict, optional): The JSON payload to send with the request. Defaults to None.
        params (dict, optional): Query parameters to include in the request. Defaults to None.
        headers (dict, optional): Additional HTTP headers to include in the request. Defaults to None.

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            exceptions.JfrogAuthenticationError: If the client is not authenticated (no API token found).
            exceptions.JfrogAPIError: If the API request fails with a other then 2xx status code.
        """
        if self._token is None:
            raise exceptions.JfrogAuthenticationError(
                "Jfrog session is not authenticated. No API token found."
            )

        response = requests.request(
            method=request_type.value,
            url=self.base_url + service_endpoint,
            json=data,
            headers=headers,
            proxies=proxies,
            verify=False,
        )

        if response.status_code == 401:  # Token expired or invalid
            log.warning("Token might have expired. Regenerating token and retrying...")
            self.login()  # Regenerate token
            headers["Authorization"] = f"Bearer {self._token}"
            response = requests.request(
                method=request_type.value,
                url=self.base_url + service_endpoint,
                json=data,
                headers=headers,
                proxies=proxies,
                verify=False,
            )

        if not response.ok:
            log.error(
                f"API call failed. Status Code: {response.status_code}, Response: {response.text}"
            )
            raise exceptions.JfrogAPIError(f"Error making API call: {response.text}")

        return response

    def login(self):
        """
        Log in the user with the provided credentials(Token)

        This method authenticates the user with JFrog using the provided username and password
        or an API token.

        Raises:
            exceptions.JfrogAuthenticationError: If the login process fails due to invalid token.
        """
        # Token created with scope="member-of-groups:*", is working for creating repo
        # But, with same token security policty creation is failing
        # Tried with scope="member-of-groups:readers" and "member-of-groups:admins" but no luck
        # Hence, proceeding with hardcoded token which is generated with admin user for an year as of now.
        # generate_api_token method is created to get token, and token generation is working.
        self._token = self.generate_api_token(self.username, self.password)
        self._token = "eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYiLCJraWQiOiJtU1R5S3NzMDZjTE4xdkNCV05mcjRyTHZxbUQ2Q2pYbzliNFl3ckphYTE0In0.eyJzdWIiOiJqZmFjQDAxanF6MHl0NGIzOTE5MTFyeDVjNG0wczl5L3VzZXJzL2thbWF0aHNoIiwic2NwIjoiYXBwbGllZC1wZXJtaXNzaW9ucy9hZG1pbiIsImF1ZCI6IipAKiIsImlzcyI6ImpmZmVAMDFqcXoweXQ0YjM5MTkxMXJ4NWM0bTBzOXkiLCJpYXQiOjE3NDM3Nzc3NTUsImp0aSI6IjQxNmEwYjk1LTgzNGItNDc5Yy1hNWEzLTY5ZDIwMTU2MTc4MyIsInRpZCI6ImEwbXQyZGd4cXppNWgifQ.DVmWOXVMWOuS9DjKpEZQC0hDdY0g86HO_94jiqQnRsedZ2b8cCLCH4ouF0JRlKrkt8Fl1OEaSStc5Q4kXNUnL-k3pJNNapF2JJJxMoj4FbN1wkj7vj04Q2diIsIs-oEKV6GaIDh2Z7ZHGrpNUZdY49sA5GYZtveHtD1xCEyEUnc122j5lc5cNkoJD5losUhiHDEBONMH9NZUj1PravB7wJSi0eS_ERpyp5cSrldgnRVGvVPQnYV5bgQC4xgI6WT0Tlp6AMydYj5sGkYNeJklYR2QNH8piiZJLZL8YhcuX41wTYacAKJslx-FYakpWFUJJoPgwPBH_s3tQKkLf6emQg"
        self.headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def create_repository(self, repo_name, package_type="docker", rclass="local", xray_index=True):
        """
        Create a repository in JFrog Artifactory.

        Args:
            repo_name (str): The name of the repository to create.
            package_type (str, optional): The type of package for the repository. Defaults to "docker".
            rclass (str, optional): The repository class. Defaults to "local".
            xray_index (bool, optional): Whether to enable Xray indexing for the repository. Defaults to True.

        Returns:
            dict: The response JSON from the API call.

        Raises:
            exceptions.JfrogAPIError: If the API request to create the repository fails.
        """
        payload = {
            "key": repo_name,
            "packageType": package_type,
            "rclass": rclass,
            "xrayIndex": xray_index,
        }

        try:
            log.info(f"Creating repository '{repo_name}' with payload: {payload}")
            response = self._make_request(
                request_type=enums.HttpRequestType.PUT,
                service_endpoint=enums.JfrogEndpoints.CREATE_OR_FETCH_REPO.value.format(repo_name),
                data=payload,
                headers=self.headers,
            )
            if response.status_code == 200 or response.status_code == 201:
                log.info(f"Successfully created repository '{repo_name}'.")
            else:
                log.error(
                    f"Failed to create repository '{repo_name}'. "
                    f"Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(
                    f"Error creating repository '{repo_name}': {response.text}"
                )
        except requests.RequestException as error:
            log.error(f"Error while creating repository '{repo_name}': {error}")
            raise exceptions.JfrogAPIError(f"Error creating repository '{repo_name}': {error}")

        return response.text

    def get_repository(self, repo_name):
        """
        Get details of a repository in JFrog Artifactory.

        Args:
            repo_name (str): The name of the repository.

        Returns:
            dict: The repository details.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        try:
            log.info(f"Fetching details for repository '{repo_name}'.")
            response = self._make_request(
                request_type=enums.HttpRequestType.GET,
                service_endpoint=enums.JfrogEndpoints.CREATE_OR_FETCH_REPO.value.format(repo_name),
                headers=self.headers,
            )

            if response.status_code == 200:
                log.info(f"Successfully fetched details for repository '{repo_name}'.")
                return response.json()
            else:
                log.error(
                    f"Failed to fetch repository details. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(
                    f"Error fetching repository details: {response.text}"
                )
        except requests.RequestException as e:
            log.error(f"Error while fetching repository details: {e}")
            raise exceptions.JfrogAPIError(f"Error fetching repository details: {e}")

    def create_security_policy(
        self, policy_name, description="Security Policy", min_severity="high"
    ):
        """
        Create a security policy in JFrog Xray.

        Args:
            policy_name (str): The name of the policy.
            description (str): The description of the policy.
            min_severity (str, optional): The minimum severity level. Defaults to "high".

        Returns:
            dict: The response JSON from the API call.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        payload = {
            "name": policy_name,
            "description": description,
            "type": "security",
            "rules": [
                {
                    "name": "some_rule",
                    "criteria": {
                        "malicious_package": False,
                        "fix_version_dependant": False,
                        "min_severity": min_severity,
                    },
                    "actions": {
                        "mails": [],
                        "webhooks": [],
                        "fail_build": False,
                        "block_release_bundle_distribution": False,
                        "block_release_bundle_promotion": False,
                        "notify_deployer": False,
                        "notify_watch_recipients": False,
                        "create_ticket_enabled": False,
                        "block_download": {"active": False, "unscanned": False},
                    },
                    "priority": 1,
                }
            ],
        }

        try:
            log.info(f"Creating security policy '{policy_name}' with payload: {payload}")
            response = self._make_request(
                request_type=enums.HttpRequestType.POST,
                service_endpoint=enums.JfrogEndpoints.CREATE_SECURITY_POLICY.value,
                data=payload,
                headers=self.headers,
            )
            if response.status_code == 200 or response.status_code == 201:
                log.info(f"Successfully created security policy '{policy_name}'.")
                return response.text
            else:
                log.error(
                    f"Failed to create security policy. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(f"Error creating security policy: {response.text}")
        except requests.RequestException as e:
            log.error(f"Error while creating security policy: {e}")
            raise exceptions.JfrogAPIError(f"Error creating security policy: {e}")

    def create_watch(self, watch_name, repo_name, policy_name, description="Watch Creation"):
        """
        Create a watch in JFrog Xray to link a policy and repository.

        Args:
            watch_name (str): The name of the watch.
            description (str): The description of the watch.
            repo_name (str): The name of the repository.
            policy_name (str): The name of the policy to link.

        Returns:
            dict: The response JSON from the API call.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        payload = {
            "general_data": {"name": watch_name, "description": description, "active": True},
            "project_resources": {
                "resources": [
                    {
                        "type": "repository",
                        "bin_mgr_id": "default",
                        "name": repo_name,
                        "filters": [{"type": "regex", "value": ".*"}],
                    }
                ]
            },
            "assigned_policies": [{"name": policy_name, "type": "security"}],
        }

        try:
            log.info(f"Creating watch '{watch_name}' with payload: {payload}")
            response = self._make_request(
                request_type=enums.HttpRequestType.POST,
                service_endpoint=enums.JfrogEndpoints.CREATE_WATCH.value,
                data=payload,
                headers=self.headers,
            )

            if response.status_code == 200 or response.status_code == 201:
                log.info(f"Successfully created watch '{watch_name}'.")
                return response.text
            else:
                log.error(
                    f"Failed to create watch. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(f"Error creating watch: {response.text}")
        except requests.RequestException as e:
            log.error(f"Error while creating watch: {e}")
            raise exceptions.JfrogAPIError(f"Error creating watch: {e}")

    def check_scan_status(self, repo_name, artifact_path):
        """
        Check the scan status of an artifact in JFrog Xray.

        Args:
            repo_name (str): The name of the repository.
            artifact_path (str): The path of the artifact.

        Returns:
            str: The scan status of the artifact.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        payload = {"repo": repo_name, "path": artifact_path}

        try:
            log.info(
                f"Checking scan status for artifact '{artifact_path}' in repository '{repo_name}' with payload: {payload}"
            )
            response = self._make_request(
                request_type=enums.HttpRequestType.POST,
                service_endpoint=enums.JfrogEndpoints.GET_SCAN_STATUS.value,
                data=payload,
                headers=self.headers,
            )

            if response.status_code == 200:
                scan_status = response.json().get("overall", {}).get("status", "UNKNOWN")
                log.info(f"Scan status for artifact '{artifact_path}': {scan_status}")
                return scan_status
            else:
                log.error(
                    f"Failed to check scan status. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(f"Error checking scan status: {response.text}")
        except requests.RequestException as e:
            log.error(f"Error while checking scan status: {e}")
            raise exceptions.JfrogAPIError(f"Error checking scan status: {e}")

    def get_violations(self, watch_name, repo_name, artifact_path):
        """
        Get violations for a scanned artifact in JFrog Xray.

        Args:
            watch_name (str): The name of the watch.
            repo_name (str): The name of the repository.
            artifact_path (str): The path of the artifact.

        Returns:
            dict: The violations data.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        payload = {
            "filters": {
                "watch_name": watch_name,
                "violation_type": "security",
                "min_severity": "High",
                "resources": {"artifacts": [{"repo": repo_name, "path": artifact_path}]},
            },
            "pagination": {"order_by": "created", "direction": "asc", "limit": 100, "offset": 1},
        }

        try:
            log.info(
                f"Fetching violations for artifact '{artifact_path}' in repository '{repo_name}' with payload: {payload}"
            )
            response = self._make_request(
                request_type=enums.HttpRequestType.POST,
                service_endpoint=enums.JfrogEndpoints.GET_VIOLATIONS.value,
                data=payload,
                headers=self.headers,
            )
            if response.status_code == 200:
                violations = response.json()
                log.info(f"Successfully fetched violations for artifact '{artifact_path}'.")
                return violations
            else:
                log.error(
                    f"Failed to fetch violations. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(f"Error fetching violations: {response.text}")
        except requests.RequestException as e:
            log.error(f"Error while fetching violations: {e}")
            raise exceptions.JfrogAPIError(f"Error fetching violations: {e}")

    def generate_api_token(
        self, username, password, scope="member-of-groups:*", expires_in=3600000
    ):
        """
        Generate an API token for the specified user.

        Args:
            username (str): The username for which to generate the token.
            password (str): The password for the user.
            scope (str, optional): The scope of the token. Defaults to "member-of-groups:*".
            expires_in (int, optional): Token expiration time in seconds. Defaults to 3600.

        Returns:
            str: The generated API token.

        Raises:
            exceptions.JfrogAPIError: If the API request fails.
        """
        payload = {"username": username, "scope": scope, "expires_in": expires_in}

        try:
            log.info(f"Generating API token for user '{username}'.")
            response = requests.post(
                url=f"{self.base_url}/artifactory/api/security/token",
                auth=(username, password),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=payload,
                verify=False,
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
                log.info(f"Successfully generated API token for user '{username}'.")
                return token
            else:
                log.error(
                    f"Failed to generate API token. Status Code: {response.status_code}, Response: {response.text}"
                )
                raise exceptions.JfrogAPIError(f"Error generating API token: {response.text}")
        except requests.RequestException as e:
            log.error(f"Error while generating API token: {e}")
            raise exceptions.JfrogAPIError(f"Error generating API token: {e}")
