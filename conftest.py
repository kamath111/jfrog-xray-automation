"""
Author: Shwetha Kamath
This module provides pytest fixtures and hooks for configuring
 and managing the JFrog Artifactory/Xray automation framework.

Purpose:
- To define and manage pytest fixtures for test configuration, 
logging, WebDriver setup and JFrog-specific operations.
- To implement pytest hooks for session-level and test-level operations,
 such as logging test metadata, attaching artifacts, and generating reports.
"""

import os
from datetime import datetime

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from util import logging
from util.config_utils import merge_config_with_cli
from util.conftest_helper import parse_args
from util.logging import set_up_logging

log = logging.get_main_logger()

# Global variables to track test session details
session_start_time = None
session_end_time = None
total_tests = 0
passed_tests = 0
failed_tests = 0


def pytest_addoption(parser):
    """
    Hook to add custom CLI options to pytest.
    """
    parse_args(parser)


@pytest.fixture(scope="session", autouse=True)
def final_config(pytestconfig):
    """
    Provide the final configuration as a pytest fixture.
    Args:
        pytestconfig: Pytest configuration object.
    Returns:
        dict: Final configuration values.
    """
    return merge_config_with_cli(pytestconfig, config_file="test_data/config.yaml")


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """
    Set up logging for the test session.
    Ensure the 'results' folder exists and store session logs
      in 'results/full.log'.
    """
    results_dir = "results"  # Directory where logs and artifacts will be stored
    log_level = "DEBUG"  # Set the desired log level

    # Ensure the 'results' folder exists
    os.makedirs(results_dir, exist_ok=True)

    # Set up session-level logging
    set_up_logging(log_level, results_dir, None)
    return results_dir


@pytest.fixture(scope="function", autouse=True)
def test_artifacts_dir(request):
    """
    Create a folder for each test inside the 'results' directory.
    The folder name matches the test name, and a 'screenshot'
    subfolder is created.
    """
    results_dir = "results"
    test_name = request.node.name
    test_dir = os.path.join(results_dir, test_name)

    # Ensure the test folder exists
    os.makedirs(test_dir, exist_ok=True)

    # Create a 'screenshot' subfolder inside the test folder
    screenshot_dir = os.path.join(test_dir, "screenshot")
    os.makedirs(screenshot_dir, exist_ok=True)

    # Provide the test folder and screenshot folder paths to the test
    return {"test_dir": test_dir, "screenshot_dir": screenshot_dir}


def pytest_sessionstart(session):
    """
    Hook to initialize session start time.
    """
    global session_start_time
    session_start_time = datetime.now()


def pytest_sessionfinish(session, exitstatus):
    """
    Hook to calculate and log session details at the end of the test run.
    """
    global session_end_time, total_tests, passed_tests, failed_tests
    session_end_time = datetime.now()

    # Calculate test duration
    duration = session_end_time - session_start_time

    # Calculate pass and fail percentages
    pass_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    fail_percentage = (failed_tests / total_tests) * 100 if total_tests > 0 else 0

    # Log session details
    log.info("\nTest Session Summary:")
    log.info(f"Start Time: {session_start_time}")
    log.info(f"End Time: {session_end_time}")
    log.info(f"Duration: {duration}")
    log.info(f"Total Tests: {total_tests}")
    log.info(f"Passed: {passed_tests}")
    log.info(f"Failed: {failed_tests}")
    log.info(f"Pass Percentage: {pass_percentage:.2f}%")
    log.info(f"Fail Percentage: {fail_percentage:.2f}%")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Ensure JUnit XML uses xunit2 format and enable user_properties.
    """
    junitxml_path = config.getoption("--junitxml")
    if junitxml_path:
        log.info(f"JUnit XML report will be saved to: {junitxml_path}")
        config.option.junit_family = "xunit2"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    """
    Add metadata to the JUnit XML report using user_properties.
    """
    if report.when == "call":
        # Add metadata to the JUnit XML report
        if hasattr(report, "user_properties"):
            report.user_properties.append(
                ("test_id", getattr(report, "test_id", "No Test ID Provided"))
            )
            report.user_properties.append(
                ("objective", getattr(report, "objective", "No Objective Provided"))
            )
            report.user_properties.append(
                ("description", getattr(report, "description", "No Description Provided"))
            )
            report.user_properties.append(
                ("precondition", getattr(report, "precondition", "No Precondition Provided"))
            )
            report.user_properties.append(
                (
                    "expected_result",
                    getattr(report, "expected_result", "No Expected Result Provided"),
                )
            )

        # Add failure-specific details
        if report.failed:
            report.user_properties.append(("failure_reason", report.longreprtext))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to track test results and attach logs and screenshots to JUnit XML and Allure Report.
    """
    global total_tests, passed_tests, failed_tests

    # Execute all other hooks to obtain the report object
    outcome = yield
    report = outcome.get_result()

    # Track test results
    if report.when == "call":
        total_tests += 1
        if report.passed:
            passed_tests += 1
        elif report.failed:
            failed_tests += 1

        # Attach the full.log file to Allure Report (for all tests)
        log_file_path = "results/full.log"
        if os.path.exists(log_file_path):
            with open(log_file_path, "r") as log_file:
                allure.attach(
                    log_file.read(), name="Full Log", attachment_type=allure.attachment_type.TEXT
                )
                log.info("Full log attached to Allure report.")
                # Add log details to JUnit XML
                report.user_properties.append(("log", log_file.read()))
        else:
            log.error(f"Log file not found at: {log_file_path}")

        # Attach a screenshot only if the test failed
        if report.failed:
            screenshot_dir = item.funcargs["test_artifacts_dir"]["screenshot_dir"]
            screenshot_path = os.path.join(screenshot_dir, "final_state.png")
            driver = item.funcargs.get("driver")
            if driver:
                driver.save_screenshot(screenshot_path)
                log.info(f"Screenshot saved at: {screenshot_path}")
                if os.path.exists(screenshot_path):
                    with open(screenshot_path, "rb") as image_file:
                        try:
                            allure.attach(
                                image_file.read(),
                                name="Failure Screenshot",
                                attachment_type=allure.attachment_type.PNG,
                            )
                            log.info("Screenshot successfully attached to Allure report.")
                            report.user_properties.append(("screenshot", screenshot_path))
                        except Exception as error:
                            log.error(f"Failed to attach screenshot to Allure report: {error}")
                else:
                    log.error(f"Screenshot not found at: {screenshot_path}")
            else:
                log.error("Driver is not available. Screenshot cannot be captured.")


@pytest.fixture(scope="function", autouse=True)
def driver():
    """
    Provide a Selenium WebDriver instance for each test function.

    This fixture initializes a headless Firefox WebDriver instance,
      maximizes the browser window,
    and ensures that the WebDriver is properly closed after
      the test execution.

    Yields:
        WebDriver: A Selenium WebDriver instance for
        interacting with the browser.

    Note:
        - The 'geckodriver' executable must be present in the
          'drivers' directory within the current working directory.
        - Ensure that the Firefox browser is installed on the system.
    """
    options = Options()
    options.add_argument("--headless")
    driver_path = os.path.join(os.getcwd(), "drivers", "geckodriver")
    service = Service(driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(scope="function", autouse=True)
def log_test_metadata(request):
    """
    Automatically log test metadata
    (test ID, objective, expected result, description, precondition)
    for each test function and attach it to Allure Report.
    """
    metadata = request.node.get_closest_marker("test_metadata")
    if metadata:
        test_id = metadata.kwargs.get("test_id", request.node.name)
        objective = metadata.kwargs.get("objective", "No objective provided.")
        description = metadata.kwargs.get("description", "No description provided.")
        precondition = metadata.kwargs.get("precondition", "No precondition provided.")
        expected_result = metadata.kwargs.get("expected_result", "No expected result provided.")
    else:
        # Default values if no metadata is provided
        test_id = request.node.name
        objective = "No objective provided."
        description = "No description provided."
        precondition = "No precondition provided."
        expected_result = "No expected result provided."

    # Log metadata to the full.log file
    log.info("Logging test metadata:")
    log.info(f"Test ID: {test_id}")
    log.info(f"Objective: {objective}")
    log.info(f"Description: {description}")
    log.info(f"Precondition: {precondition}")
    log.info(f"Expected Result: {expected_result}")

    # Attach metadata to Allure Report
    allure.dynamic.title(test_id)
    allure.dynamic.description(
        f"**Objective:** {objective}\n\n**Description:** {description}\n\n**Precondition:** {precondition}\n\n**Expected Result:** {expected_result}"
    )


@pytest.fixture(scope="function", autouse=True)
def jfrog_config(final_config):
    """
    Provide a JFrog configuration dictionary for each test function.

    This fixture generates a dynamic configuration for JFrog
      Artifactory and Xray operations
    by combining values from the 'final_config' fixture

    The configuration includes details such as repository name,
      authentication credentials,
    image tags, artifact paths, and other JFrog-specific parameters
      required for test execution.

    Args:
        final_config (dict): The final configuration dictionary loaded
          from the YAML file and merged with CLI options.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    repo_name = final_config["repository"]["repoName"]
    username = final_config["authentication"]["user"]
    password = final_config["authentication"]["password"]
    base_url = final_config["authentication"]["baseUrl"]
    custom_tag = final_config["repository"]["customTag"]
    custom_image_name = final_config["repository"]["customImageName"]
    watch_name = final_config["watch"]["watchName"]
    policy_name = final_config["policy"]["policyName"]
    # Repo name should be unique for each test run to avoid conflicts
    # (as duplicate name is not allowed)
    # Uncomment the following line if you want to append timestamp to repo_name(to have unique repo names)
    # For this test, I am using docker-local as repo name as provided in instructions
    # repo_name = f"{repo_name}-{timestamp}"
    # watch, policy names are created dynamic as below appended with timestamp
    watch_name = f"{watch_name}-{timestamp}"
    policy_name = f"{policy_name}-{timestamp}"
    source_image = f"{custom_image_name}:{custom_tag}"
    registry_url = final_config["authentication"]["baseUrl"].strip("/")
    registry_url = registry_url.replace("https://", "")
    target_image = f"{registry_url}/{repo_name}/{custom_image_name}:{custom_tag}"
    artifact_path = f"{custom_image_name}/{custom_tag}/manifest.json"
    artifact_name = f"{custom_image_name}/{custom_tag}"
    return {
        "repo_name": repo_name,
        "username": username,
        "password": password,
        "base_url": base_url,
        "custom_tag": custom_tag,
        "custom_image_name": custom_image_name,
        "watch_name": watch_name,
        "policy_name": policy_name,
        "source_image": source_image,
        "registry_url": registry_url,
        "target_image": target_image,
        "artifact_path": artifact_path,
        "artifact_name": artifact_name,
    }
