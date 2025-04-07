## Design Strategy for JFrog Artifactory/Xray Automation Framework:

    This design strategy outlines the architecture, components, and best practices for building and maintaining an automation framework for JFrog Artifactory and Xray, based on the     provided framework.

1. Objectives
    Automate end-to-end workflows for JFrog Artifactory and Xray.
    Validate Docker image uploads, security scans, and policy violations.
    Provide API and UI-based validations for comprehensive test coverage.
    Ensure modularity, scalability, and maintainability of the framework.

2. Framework Architecture/Project structure

       Layered Architecture:
        Test Layer: Contains test cases written using pytest for end-to-end workflows.
        Service Layer: Encapsulates API interactions with JFrog Artifactory and Xray.
        UI Layer: Implements Selenium-based Page Object Models (POM) for UI automation.
        Utility Layer: Provides reusable utilities for logging, subprocess handling, and waiting for scan completion.
       Extensibility: The framework supports adding new workflows, API methods, and page objects with minimal changes
   
    2.1 Layers of the Framework

   

        jfrog_xray/testsuites
        Test Layer:
        Contains test cases written using pytest.
        Focuses on high-level workflows (e.g., Docker image upload, security policy creation, violation validation).
        Example: test_jfrog_xray_e2e_violation_validation.py

        jfrog_xray/integration_core
        Service Layer:
        Encapsulates API interactions with JFrog Artifactory and Xray.
        Provides reusable methods for operations like repository creation, token generation, and policy management.
        Example: jfrog_service.py.

        Client Layer:
        Handles interactions with external tools like Docker.
        Provides methods for Docker image pull, tag, push, and login.
        Example: clients.py.

        jfrog_xray/page_objects
        UI Layer:
        Encapsulates Selenium-based UI interactions with JFrog's web interface.
        Provides page object models for login, dashboard, and violations pages.
        Example: login_page.py, page_objects/dashboard_page.py.

        jfrog_xray/utility
        Utility Layer:
        Contains helper functions for logging, waiting for scan completion, and other reusable utilities.
        Example: logging.py, jfrog_scan_helper.py.

        Test data layer:
        jfrog_xray/drivers
        gecko driver binary to run UI tests
        jfrog_xray/test_data:
        Configuration details for the test

        Results layer:
        jfrog_xray/results
        Dynamically during test run, results folder will be created
        full.log - Complete log of test run
        screenshots - ui screenshot of ui interactions
        And reports

        jfrog_xray/conftest
        Test level fixtures
        Reporting Layer:
        Allure and junitxml customised reporting

4. Key Components
    3.1 Test Cases
        Written in pytest for modularity and scalability.
        Use @pytest.mark for metadata and grouping.

        Example:
        @pytest.mark.test_metadata(
            test_id="test_docker_image_scan_e2e",
            objective="Test E2E validation for uploading a Docker image to JFrog Artifactory, scanning it with JFrog Xray, and validating the results."
        )
        @pytest.mark.e2e
        def test_docker_image_scan_e2e(jfrog_config, driver, test_artifacts_dir):
            ...

    3.2 API Interactions
   
        Encapsulated in the JFrogAPIClient class.
        Provides methods for:
        Token generation (generate_api_token).
        Repository creation (create_repository).
        Security policy creation (create_security_policy).
        Watch creation (create_watch).
        Violation retrieval (get_violations).

    3.3 UI Interactions
   
        Implemented using the Page Object Model (POM) pattern.
        Each page (e.g., Login, Dashboard, Violations) has its own class with methods for interacting with UI elements.
        Example:
        login_page = LoginPage(driver, screenshot_dir)
        login_page.login(jfrog_config['username'], jfrog_config['password'])

    3.4 Docker Client
   
        Provides methods for Docker operations:
        Pulling images (pull_image).
        Tagging images (tag_image).
        Pushing images (push_image).
        Logging into the Docker registry (login_to_registry).

    3.5 Logging
   
        Centralized logging using a custom logger (util/logging.py).
        Logs are categorized by severity (INFO, WARNING, ERROR) and include detailed messages for debugging.

   3.6 Configuration Management
   
        Test configurations are passed as dictionaries (jfrog_config).
        Includes details like:
        JFrog credentials (username, password).
        Repository and policy names (repo_name, policy_name).
        Docker image details (source_image, target_image).

6. Workflow Design
   
    4.1 End-to-End Workflow

        Repository Creation:
        Create a Docker repository in JFrog Artifactory using the API.
        Validate the repository creation by fetching its details.

        Docker Image Upload:
        Pull a Docker image from a public registry.
        Tag the image with the target repository path.
        Push the image to the created repository.
        Security Policy and Watch Creation:

        Create a security policy in JFrog Xray using the API.
        Create a watch in JFrog Xray and associate it with the repository and policy.
   
        Scan Completion:
        Wait for the scan to complete using helper methods.
        Validate the scan status via API.

        Violation Validation:
        Retrieve violations using the API.
        Validate the number

        UI Validation:
        Log in to the JFrog UI.
        Navigate to the Xray section and validate violations displayed in the UI.

8. Best Practices
   
    5.1 Modular Design
   
        Separate API, UI, and Docker interactions into distinct layers.
        Use reusable methods for common operations (e.g., token generation, repository creation).

    5.2 Error Handling
   
        Implement robust error handling with retries for transient failures.

        if response.status_code == 401:  # Token expired or invalid
        log.warning("Token might have expired. Regenerating token and retrying...")
            self.login()

    5.3 Logging
   
        Use structured logging for better traceability.
        Include detailed messages for each step of the workflow.

    5.4 Test Metadata
   
        Use @pytest.mark.test_metadata to document test objectives, preconditions, and expected results.

    5.5 Configuration Management
   
        Store sensitive information (e.g., credentials) securely.
        Use environment variables or encrypted configuration files.

    5.6 Scalability
   
        Design the framework to support additional workflows is easier
        Add new page objects and API methods as needed in same hierarchy

    5.7 Best Practises
   
        Code Quality and Conventions:

        - **Pre-Commit Hooks**:
          - Automatically runs checks before committing code to the repository.
          - Ensures code formatting, linting, and import sorting are enforced.
          - Configured using the `.pre-commit-config.yaml`

        - **Flake8**:
          - Lints Python code for style guide violations, programming errors, and code complexity issues.
          - Configured using the `.flake8` file to define rules like maximum line

        - **Black**:
          - Formats Python code to ensure consistency across the project.
          - Integrated as a pre-commit hook.

        - **isort**:
          - Sorts imports in Python files to maintain a consistent order.
          - Integrated as a pre-commit hook.

        These tools are seamlessly integrated into the development workflow to maintain high code quality.

6. Tools and Technologies
   
        Programming Language: Python 3.8
        Test Framework: pytest
        API Client: requests
        UI Automation: Selenium WebDriver
        Docker Client: Python Docker SDK
        Logging: Python logging module
        Configuration Management: YAML or JSON files
        Reporting: Alure and junitxml

7. Usage of Patterns
   
        Page Object Model (POM): Used for UI automation to encapsulate page-specific logic and actions.
        Factory Pattern: Used for creating reusable API clients (e.g., JFrogAPIClient).
        Command Pattern: Docker operations (e.g., pull, push) are executed using subprocess commands encapsulated in the DockerClient class.

8. Reporting
   
        Allure Reports:
        Interactive HTML reports generated for test execution.
        Includes test metadata, logs, and screenshots.
        JUnit XML Reports:
        Machine-readable reports for CI/CD integration.
        Summary Reports:
        High-level summaries of test results (e.g., pass/fail counts) are logged and shared with stakeholders.

10. Future Enhancements

    Parallel Execution:
    Use pytest-xdist for running tests in parallel.

Integration with CI/CD:

    Integrate the framework with GitHub Actions for automated test execution.


