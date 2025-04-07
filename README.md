## Table of Contents
1. [Introduction](#jfrog-xray-automation)
2. [Code Organization](#code-organization)
3. [How to Add a Test Suite](#how-to-add-a-test-suite)
4. [Requirements](#requirements)
5. [Prerequisites](#prerequisites)
6. [Code Quality Tools](#codequalitytools)
7. [Running Tests](#running-tests)
8. [Result of Test Run](#result-of-test-run)
9. [Reports of Test Run](#reports-of-test-run)
10. [Viewing Allure Report](#viewing-allure-report)
11. [Troubleshooting](#troubleshooting)

# JFrog Xray Automation
- The jfrog_xray automation framework contains the JFrog library, which enables interacting with Jfrog end product(xray).
- The repository also contains the E2E/API/UI test suites for validating Jfrog Xray product functionalities and workflows.

## General Principles:
- Tests are run from the jfrog_xray project root folder.
- Test suites are written in Python 3 and use pytest as the base framework, with customizations tailored for the specific product.
- Tests can interact with JFrog interfaces (API and UI) as well as third-party tools such as Docker.

## Code organization:
- `drivers`: Driver binaries required for browser-based automation or UI testing.
Contents:
geckodriver: A WebDriver for Mozilla Firefox, used for automating browser interactions in UI tests.
Usage:
Ensure the driver is executable and correctly configured in the system's PATH

- `integration_core/`: This folder contains the core modules and utilities required for interacting with JFrog Xray APIs, any applications example: docker, handling exceptions, and managing helper functions for the automation framework.

  Subdirectories and Files:
  
     constants.py:
     Defines constants used across the framework, such as scan intervals and timeouts for JFrog Xray operations.

     enums.py:
     Contains enumerations for standardizing request types, endpoints, and other fixed values used in the framework.

     exceptions.py:
     Defines custom exception classes for handling errors specific to JFrog Xray operations.

     helpers/:
     jfrog_helpers.py:
     Provides helper functions for common tasks like authentication, repository creation, 
     artifact uploads, and Xray scans.

     models/:
     clients.py:
     Contains data models and client classes for interacting with JFrog services/third party models- Docker

     utils/:
     jfrog_service.py:
     Implements the JFrogAPIClient class, which provides methods for interacting with JFrog APIs. Key functionalities include:
     Logging in to JFrog.
     Creating repositories and security policies.
     Managing watches.
     Checking scan statuses and retrieving violations.

- `page_objects/`: This folder contains Page Object Model (POM) classes for automating interactions with the JFrog Xray web interface. Each page class encapsulates the locators and methods for interacting with a specific page or component of the JFrog Xray web interface.
These classes are used in test scripts to perform actions like logging in, navigating to sections, and validating UI elements.

  Subdirectories and Files:
    page_objects.py:
    Serves as the base class for all page objects in the framework. It provides reusable methods for interacting with web elements, such as clicking elements, entering text, taking       screenshots, and waiting for elements.

    login_page.py:
    Represents the login page of the JFrog Artifactory web interface.

    dashboard_page.py:
    Represents the Dashboard page in the JFrog Artifactory web interface.

    violations_page.py:
    Represents the Violations page in the JFrog Artifactory web interface.

- `test_data/`: This folder contains configuration files and test data required for running JFrog Xray automation tests. It centralizes all the necessary parameters, credentials, and settings for seamless test execution.
  
  config.yaml:
  Provides configuration details for JFrog Artifactory and Xray, including repository settings, authentication credentials, and security policies.
  This file is loaded by the test framework to configure the environment and test parameters dynamically and these values can be overriden with Clis(during test run)

- `testsuites/`: This folder contains the end-to-end (E2E)/api/api test suites for validating JFrog Xray workflows. These tests are written using the pytest framework and are designed to validate the integration between JFrog Artifactory and Xray.
These tests validate both API and UI workflows, ensuring the correctness of JFrog Xray's functionality.

- `util/`: This folder contains utility modules that provide helper functions and reusable components for various aspects of the JFrog Xray automation framework. These utilities support logging, subprocess management, UI interactions, and JFrog Xray-specific operations and test helpers.
  config_utils.py:
    Provides utility functions for managing and parsing configuration files used in the framework.

  conftest_helper.py:
    Contains helper functions for parsing command-line arguments and setting up test configurations. Adds options like repo setting security policies, and specifying artifact paths.

  exception_util.py:
    Defines utility functions for handling and logging exceptions during test execution/test helpers

  jfrog_scan_helper.py:
    Provides test helper functions for managing JFrog Xray scan operations.

  logging.py:
    Implements logging utilities for the framework.
    Sets up logging configurations.
    Provides functions for logging exceptions, masking sensitive data, and detailed logging.

  subprocess_helper.py:
    Provides helper functions for managing subprocesses, such as executing shell commands and capturing their output.

  ui_helpers.py:
    Contains common helper functions for UI-based test suites.

- `conftest/`: File provides pytest fixtures and hooks for configuring and managing the JFrog Artifactory/Xray automation framework. It centralizes test session setup, logging, WebDriver initialization, and JFrog-specific configurations.
It simplifies test setup by providing reusable fixtures and hooks for logging, configuration, and WebDriver management.

- `pytest.ini`: File is a configuration file for the pytest framework. It defines custom markers and global settings for organizing and running tests in the JFrog Xray automation framework.

- `requirements.txt`: File lists all the Python dependencies required for the JFrog Xray automation framework. It ensures that all necessary libraries and their compatible versions are installed for the framework to function correctly.

## How to add a test suite:
- Navigate to the testsuites folder.[jfrog_xray/testsuites]
- Create a new Python file for your test suite. For example:
  in jfrog_xray/testsuites. See `test_jfrog_xray_e2e_violation_validation.py` as a basic example.
- Import required library files, call existing functions. 
  Example:
  import pytest
  from util.jfrog_scan_helper import scan_artifact
  from util.logging import log_test_metadata
- Write your test cases using the pytest framework. Use descriptive function names and include relevant assertions.(Reference file: jfrog_xray/testsuites/test_jfrog_xray_e2e_violation_validation.py)
- Use markers for running and grouping tests, test_matadata fixture to add in report
- Leverage the fixture defined in conftest.py for logging, configuration, or WebDriver setup
- Follow naming conventions for test files and functions (e.g., test_*.py and test_*) 

## Requirements:
- Assumed environment used: Ubuntu Ubuntu 20.04.5 LTS with updated package versions (i.e. Docker).
- A stable Python 3.8 release (i.e. Python 3.8.10), headers `sudo apt-get install python3.8-dev` and venv `sudo apt install python3.8-venv`. Reference: https://docs.python.org/3/using/
- Use a virtual environment to avoid conflicts with system packages or instability from other installations.
- Set up a virtual environment using your preferred way (venv, virtualenv). For example:

  `python3.8 -m venv venv_py38`

  `source venv_py38/bin/activate`

  Note that instead of using activate/deactivate, you can call `venv_py38/bin/python3.8` directly instead of `python3.8`.

- Jfron Xray automation framework uses requirements.txt to list of dependent packages. To view the currently supported version of PyTest or other required 3rd party packages refer to this file.

- Dependencies can be installed using pip:

  `python3.8 -m pip install -r requirements.txt`

## Prerequisites
Before running the JFrog Xray automation framework, ensure the following packages and tools are installed on your system:

1. System Requirements
Operating System: Ubuntu 20.04.5 LTS (or compatible Linux distribution)
Python: Python 3.8 (e.g., Python 3.8.10)

2. Required Tools and Packages
   
 a. Python and Virtual Environment
    Install Python 3.8 and required tools:
    sudo apt-get update
    sudo apt-get install python3.8 python3.8-dev python3.8-venv

    Set up a virtual environment:
    python3.8 -m venv venv_py38
    source venv_py38/bin/activate

 b. Python Dependencies:
    Install required Python packages using requirements.txt:
    python3.8 -m pip install -r requirements.txt

 c. Docker
    Install Docker for managing containerized workflows:
    sudo apt-get install docker.io

    Add your user to the Docker group to avoid using sudo:
    sudo usermod -aG docker $USER

    Verify Docker installation:
    docker --version
    docker ps

 d. Allure CLI
    Install Allure CLI for generating and viewing test reports:
    wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.20.1/allure-commandline-2.20.1.tgz
    tar -zxvf allure-commandline-2.20.1.tgz -C /opt/
    export PATH=$PATH:/opt/allure-2.20.1/bin

    Verify Allure installation:
    allure --version

 e. Firefox and Geckodriver
    Install Firefox browser:[version: Mozilla Firefox 136.0]
    sudo apt-get install firefox

    Install Geckodriver for Selenium WebDriver:
    wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
    tar -xvzf geckodriver-v0.33.0-linux64.tar.gz
    sudo mv geckodriver /usr/local/bin/
    chmod +x /usr/local/bin/geckodriver

    Verify Geckodriver installation:
    geckodriver --version

    Note:
    Drivers folder contains the geckodriver binary if you are not installing it globally.

    Ensure the results directory has appropriate write permissions:
    chmod -R 755 jfrog_xray/results

## Code Quality Tools
The JFrog Xray automation framework uses tools like pre-commit and Flake8 to ensure code quality and consistency.

- Pre-Commit Hooks
Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. It ensures that code quality checks are run automatically before committing changes to the repository.

- Setup Pre-Commit
Install pre-commit:(This is already defind as part of requirements.txt)
pip install pre-commit

Install the pre-commit hooks defined in the .pre-commit-config.yaml file:
pre-commit install

- Pre-Commit Hooks Used
The following hooks are configured in .pre-commit-config.yaml:

- black: Formats Python code to ensure consistency.
- isort: Sorts imports in Python files.
- flake8: Lints Python code for style and programming errors.
- blacken-docs: Formats Python code in documentation.
- seed-isort-config: Seeds the isort configuration with known standard library imports.

- How It Works
When you attempt to commit changes, pre-commit hooks will automatically run.
If any hook fails, the commit will be blocked until the issues are resolved.

- Skipping Pre-Commit Hooks
To skip pre-commit hooks for a specific commit, use:
git commit --no-verify

- Flake8
Flake8 is a Python linting tool that checks your code for style guide violations, programming errors, and code complexity issues.

- Install flake8:
pip install flake8

- The framework uses a .flake8 configuration file to define linting rules. The file includes:

max-line-length: Maximum allowed line length (default: 130).
max-complexity: Maximum cyclomatic complexity for functions/methods (default: 18).
select: Error codes to check (e.g., E, F, W).
ignore: Error codes to ignore (e.g., E203, E501, W503).

- Running Flake8
To lint your code using Flake8, run:
flake8 .

- Customizing Flake8
You can modify the .flake8 file to adjust linting rules. For example:
[flake8]
max-line-length = 130
max-complexity = 18
select = B,C,E,F,W,T4,B9
ignore = E203, E501, W503

- Development Workflow
Before committing changes, ensure that:

Code is formatted using black.
Imports are sorted using isort.
Code passes linting checks using flake8.

Fix any issues reported by the hooks before committing




## Running tests:
Navigate to folder: jfrog_xray

- Run all tests in a suite:
`pytest testsuites/<test_file>.py`

Replace <test_file> with actual test, example:
test_jfrog_xray_e2e_violation_validation.py 

- Run individual tests based on a pattern:
`pytest testsuites/<test_file> -m e2e`
(-m e2e is optional, to run specific test marker can be used, else all tests under test file will run)

Replace <test_file> with actual test, example:
test_jfrog_xray_e2e_violation_validation.py 

### Result of test run:(Log file and screenshots)
- All notable actions and results will be output as a log in your console.
- Use `log_level` as `DEBUG` in the test file to increase the log level from the default `INFO` log.
- The result directory is output at the beginning of a test run.  e.g. `/jfrog_xray/results`
- All tests consolidated detailed log will be added in full.log under results folder e.g. `/jfrog_xray/results/full.log`
- For All UI validations, screenshot of specific UI are taken and will be stored during run time in results folder for specific test, e.g. `/jfrog_xray/results/<test_file>/full.log`

Replace <test_file> with actual test, example:
test_jfrog_xray_e2e_violation_validation.py 
- Reference to set log_level to INFO,
e.g./`pytest testsuites/<test_file> -m e2e --alluredir=results/allure-results --junitxml=results/junit-report.xml  -v --log-cli-level=INFO`

### Reports of test run:
The JFrog Xray automation framework provides support for generating test reports in the following formats:
- Allure report
- Junitxml

Command to Generate Reports:
To generate both Allure and JUnit XML reports, use the following command<either allure or junit can be used, or both can be used together as below.>
e.g./`pytest testsuites/test_jfrog_xray_e2e_violation_validation.py -m e2e --alluredir=results/allure-results --junitxml=results/junit-report.xml  -v --log-cli-level=INFO`

Report Locations:
JUnit XML Report:
The JUnit XML report will be stored at:
`/jfrog_xray/results/junit-report.xml`

Allure Report:
Pre requisite for Allure:
Allure CLI must be installed to generate and view reports. 

The Allure results will be stored at:
`/jfrog_xray/results/allure-results`

#### Viewing Allure Report
To view the Allure report after the test run:

1. Ensure Allure CLI is installed. If not, install it using the following commands:
   ```bash
   wget https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.20.1/allure-commandline-2.20.1.tgz
  tar -zxvf allure-commandline-2.20.1.tgz -C /opt/
  export PATH=$PATH:/opt/allure-2.20.1/bin
   ```

Once the test is completed, you can serve and view the Allure report using the following steps:

1. Run the following command from the VM to serve the Allure Report:

`allure serve results/allure-results --host 0.0.0.0 --port 8080`

3. Open a browser and navigate to the following URL to view the report:
`http://<host_ip>:8080`

Replace <host_ip> with the IP address of the host machine.

# Troubleshooting
1. Allure CLI Not Found
Issue: Running allure serve results in a "command not found" error.
Solution: Ensure Allure CLI is installed and added to the system's PATH.
Verify installation:
allure --version

If not installed, follow the installation steps in the Reports of Test Run section

2. Missing geckodriver or Firefox
Issue: Tests fail with errors related to the WebDriver or browser not being found.
Solution:
Install Firefox:
sudo apt-get install firefox
version: Mozilla Firefox 136.0

Install geckodriver:
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xvzf geckodriver-v0.33.0-linux64.tar.gz

3. Python Dependency Issues
Issue: Errors occur due to missing or incompatible Python packages.
Solution:
Ensure you are using Python 3.8:
python3.8 --version
Install dependencies:
python3.8 -m pip install -r requirements.txt

4. Test Fails Due to Incorrect Configuration
Issue: Tests fail due to missing or incorrect configuration in config.yaml.
Solution:
Verify the config.yaml file contains valid values for:
repoName
user and password
baseUrl
Ensure the JFrog Artifactory/Xray instance is accessible from the test environment.

5. Allure Report Not Generated
Issue: The allure-results folder is empty after running tests.
Solution:
Ensure the --alluredir option is included in the pytest command:
pytest testsuites/<test_file>.py --alluredir=results/allure-results

Verify that the allure-pytest package is installed:
python3.8 -m pip install allure-pytest

6. Permission Denied Errors
Issue: Permission errors occur when running tests or accessing files.
Solution:
Ensure you have write permissions for the results directory:
chmod -R 755 jfrog_xray/results
Run the tests as a user with appropriate permissions.

7.  Docker Issues
Issue: Tests involving Docker fail due to Docker not being installed or accessible.
Solution:
Install Docker:
sudo apt-get install docker.io

Add your user to the Docker group:
sudo usermod -aG docker $USER

Verify Docker is running:
docker ps

8. Selenium WebDriver Errors
Issue: Selenium WebDriver fails to initialize or interact with the browser.
Solution:
Ensure the correct version of selenium is installed:
python3.8 -m pip install selenium==4.1.0
Verify that the WebDriver matches the installed browser version.

9. . Network Connectivity Issues
Issue: Tests fail due to network connectivity issues with JFrog Artifactory/Xray.
Solution:
Verify the network connection to the JFrog instance
ping <jfrog_base_url>
Check if a proxy or firewall is blocking access.

These troubleshooting steps should help resolve common issues encountered while running the JFrog Xray automation framework. 
