"""
This file contains all tests related to JFrog Artifactory and Xray
 integration, specifically for testing the end-to-end workflow of
    uploading a Docker image, scanning it with JFrog Xray, and validating
    the results against a security policy through the JFrog UI.
        Retrieve and validate the violations displayed on the Violations page.
        in the JFrog Artifactory web interface.
Author: Shwetha Kamath
"""

import time
from datetime import datetime

import pytest

from integration_core.models import clients
from integration_core.utils import jfrog_service
from page_objects.dasboard_page import DashboardPage
from page_objects.login_page import LoginPage
from page_objects.violations_page import ViolationsPage
from util import jfrog_scan_helper, logging

log = logging.get_main_logger()


@pytest.mark.test_metadata(
    test_id="test_docker_image_scan_e2e",
    objective="Test E2E validation for uploading a Docker image to JFrog Artifactory, "
    "scanning it with JFrog Xray through Jfrog Apis and validating the results against a security"
    " policy through JFrog UI.",
    description=(
        "This test verifies the complete workflow of uploading a Docker image to JFrog Artifactory, "
        "scanning it with JFrog Xray, and validating the results against a predefined security policy. "
        "The test includes repository creation, Docker image upload, security policy creation, watch creation"
        " through Jfrog Apis, "
        "and validation of violations through UI"
    ),
    precondition="Jfrog account is created for admin user before starting the test. "
    "Token for Jfrog account is available. "
    "Security policy and watch is set up in JFrog Xray. ",
    expected_result="The Docker repository is created, the image is uploaded and scanned successfully"
    " through Jfrog Apis"
    " security violations are detected and validated against the predefined policy, and only critical or"
    " high-severity violations are displayed in the JFrog Xray UI.",
)
@pytest.mark.e2e
def test_docker_image_scan_e2e(jfrog_config, driver, test_artifacts_dir):  # noqa: F811
    """
    End-to-End Test for JFrog Artifactory and Xray Integration.

    This test validates the complete workflow of uploading a Docker image to JFrog Artifactory,
    scanning it with JFrog Xray, and validating the results against a predefined security policy.
    The test includes repository creation, Docker image upload, security policy creation, watch creation
    through Jfrog Apis,
    and validation of violations through JFrog UI.

    Input Parameters:
    - jfrog_config (dict): Configuration details for interacting with JFrog Artifactory and Xray.
        - repo_name (str): Name of the Docker repository to be created.
        - username (str): Username for JFrog authentication.
        - password (str): Password or API token for JFrog authentication.
        - base_url (str): Base URL of the JFrog platform.
        - custom_tag (str): Custom tag for the Docker image.
        - custom_image_name (str): Name of the Docker image.
        - watch_name (str): Name of the watch to be created in Xray.
        - policy_name (str): Name of the security policy to be created in Xray.
        - source_image (str): Source Docker image to be pulled.
        - registry_url (str): URL of the Docker registry.
        - target_image (str): Full path of the Docker image to be pushed to Artifactory.
        - artifact_path (str): Path to the artifact in the repository.
        - artifact_name (str): Name of the artifact.

    - driver (WebDriver): Selenium WebDriver instance for interacting with the JFrog UI.
    - test_artifacts_dir (dict): Directory paths for storing test artifacts like screenshots.

    Steps:
    1. Create a Docker repository in JFrog Artifactory.
    2. Pull, tag, and push a Docker image to the created repository.
    3. Create a security policy and a watch in JFrog Xray.
    4. Wait for the scan to complete and validate the results via API calls.
    5. Log in to the JFrog UI and validate the violations displayed in the Xray section.

    Expected Results:
    - The Docker repository is created successfully in JFrog Artifactory.
    - The Docker image is uploaded and scanned successfully.
    - Security policy and watch are created successfully in JFrog Xray.
    - Violations are detected and validated against the predefined security policy.
    - The JFrog Xray UI displays violations with the correct severity levels (critical or high).
    """

    jfrog_client = jfrog_service.JFrogAPIClient(
        jfrog_config["base_url"],
        username=jfrog_config["username"],
        password=jfrog_config["password"],
    )
    jfrog_client.login()

    log.info("Step1: Create a docker repository")
    response = jfrog_client.create_repository(jfrog_config["repo_name"])
    assert (
        f"Successfully created repository '{jfrog_config['repo_name']}'" in response
    ), f"Unexpected response: {response}"
    log.info(f"Expected Result: Docker repository{jfrog_config['repo_name']} is created")
    repo_access = jfrog_client.get_repository(jfrog_config["repo_name"])
    assert (
        repo_access.get("key") == jfrog_config["repo_name"]
    ), f"Repository '{jfrog_config['repo_name']}' was not created. Response: {repo_access}"

    # Pull, tag, and push the image
    log.info("Step2: Push Docker image to JFrog Artifactory")
    docker_client = clients.DockerClient(
        username=jfrog_config["username"],
        password=jfrog_config["password"],
        registry_url=jfrog_config["registry_url"],
    )
    docker_client.pull_image(jfrog_config["source_image"])
    docker_client.login_to_registry()
    docker_client.tag_image(jfrog_config["source_image"], jfrog_config["target_image"])
    docker_client.push_image(jfrog_config["target_image"])
    log.info(
        f"Expected Result: Docker image is successfully pushed to JFrog Artifactory repository '{jfrog_config['repo_name']}'"
    )

    # Create the security policy
    log.info("Step3: Create the Security Policy")
    response = jfrog_client.create_security_policy(jfrog_config["policy_name"])
    assert '{"info":"Policy created successfully"}' in response, f"Unexpected response: {response}"
    log.info(f"Expected Result: Policy: {jfrog_config['policy_name']} created successfully")

    # Create the watch
    log.info("Step4: Create a watch")
    response = jfrog_client.create_watch(
        jfrog_config["watch_name"], jfrog_config["repo_name"], jfrog_config["policy_name"]
    )
    assert (
        '{"info":"Watch has been successfully created"}' in response
    ), f"Unexpected response: {response}"
    log.info(f"Expected Result:: Watch: {jfrog_config['watch_name']} created successfully")

    log.info("Step5: Check scan status and wait for completion")
    jfrog_scan_helper.wait_for_scan_completion(
        jfrog_client, jfrog_config["repo_name"], jfrog_config["artifact_path"]
    )
    log.info(
        "Expected Result: Scan completed successfully with status as 'Done'. Proceeding to validate violations."
    )

    log.info("Step6: Verify the violations in JFrog Xray")
    violations = jfrog_client.get_violations(
        jfrog_config["watch_name"], jfrog_config["repo_name"], jfrog_config["artifact_path"]
    )
    total_violations = violations.get("total_violations", 0)
    assert (
        total_violations > 0
    ), f"Unexpected 'total_violations' type: {type(total_violations)}. Response: {violations}"
    log.info("Expected Result: Total violations found: {}".format(total_violations))

    screenshot_dir = test_artifacts_dir["screenshot_dir"]

    # Step 1: Log in
    log.info("UI Validations")
    log.info("Step7: Logging into JFrog UI as admin user")
    driver.get(f"{jfrog_config['base_url']}/ui/login/")
    login_page = LoginPage(driver, screenshot_dir)
    login_page.login(jfrog_config["username"], jfrog_config["password"])
    log.info("Expected Result: Logged into JFrog UI")

    # Step 2: Navigate to Xray and select repository
    dashboard_page = DashboardPage(driver, screenshot_dir)
    dashboard_page.navigate_to_xray()
    driver.maximize_window()
    dashboard_page.select_repository(jfrog_config["repo_name"])

    # Step 3: Select artifact and validate violations
    violations_page = ViolationsPage(driver, screenshot_dir)
    violations_page.select_artifact(jfrog_config["artifact_name"])
    violations_page.click_policy_violations()

    # Step 4: Validate severity of violations
    log.info("Step8: Verify Violations Severity")
    table_data = violations_page.get_violations()
    allowed_severities = ["critical", "high"]
    for row in table_data:
        severity = row["severity"]
        assert severity in allowed_severities, f"Unexpected severity found: {severity}"
    log.info(
        "Expected Result: Only Critical anbd high violations are listed as policy is set to fail on critical and high severity."
    )
    log.info("Test completed successfully.")
