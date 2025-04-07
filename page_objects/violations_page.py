"""
This module defines the `ViolationsPage` class, which represents
 the Violations page 
in the JFrog Artifactory web interface.

Purpose:
- To provide locators and methods for interacting with
 elements on the Violations page.

Note:
- Ensure that the Selenium WebDriver is properly initialized
 before using this class.
- The locators and methods are specific to the JFrog
 Artifactory Violations page.
 Author: Shwetha Kamath
"""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_objects.page_objects import PageObject
from util import logging

log = logging.get_main_logger()


class ViolationsPage(PageObject):
    """
    Represents the Violations page in the JFrog Artifactory web interface.

    This class provides locators and methods to interact with
      elements on the Violations page.
    """

    ARTIFACT_NAME = lambda self, artifact_name: (By.XPATH, f"//span[text()='{artifact_name}']")
    POLICY_VIOLATIONS = (
        By.XPATH,
        "(//*[name()='svg']//*[name()='path' and contains(@d, 'M6.64893 11.8367V19.2007')])[2]",
    )
    ROWS = (By.CSS_SELECTOR, '.ag-center-cols-container [role="row"]')

    def select_artifact(self, artifact_name):
        """
        Select an artifact by its name.

        This method clicks on the artifact name and
        takes a screenshot of the artifact page.

        Args:
            artifact_name (str): The name of the artifact to select.
        """
        self.click_element(self.ARTIFACT_NAME(artifact_name))
        self.take_screenshot(f"Artifact_{artifact_name}.png")

    def click_policy_violations(self):
        """
        Click on the policy violations section.
        """
        self.click_element_javascript(self.POLICY_VIOLATIONS)
        self.take_screenshot("Policy_violations_page_click.png")

    def get_violations(self):
        """
        Retrieve violation details from the table while handling
          dynamic updates.

        This method iterates through the rows of the violations table,
          extracts details such as
        path, severity, applicability, and issue ID, and handles
          stale element issues by re-locating rows.

        Returns:
            list: A list of dictionaries containing violation details,
              where each dictionary has the keys:
                - "path": The path of the artifact.
                - "severity": The severity level of the violation.
                - "applicability": The applicability result of the violation.
                - "issue_id": The issue ID of the violation.
        """
        table_data = []
        rows = self.wait.until(EC.presence_of_all_elements_located(self.ROWS))

        for index in range(len(rows)):
            try:
                # Re-locate the rows dynamically to avoid stale element issues
                rows = self.wait.until(EC.presence_of_all_elements_located(self.ROWS))
                row = rows[index]

                # Extract data from the row
                path = row.find_element(
                    By.CSS_SELECTOR, '[col-id="paths"] .ag-cell-value div[path]'
                ).get_attribute("path")
                severity = (
                    row.find_element(By.CSS_SELECTOR, '[col-id="severity"] .ag-cell-value use')
                    .get_attribute("xlink:href")
                    .replace("#icon_", "")
                )
                applicability = row.find_element(
                    By.CSS_SELECTOR, '[col-id="applicability_result"] .ag-cell-value .tag-label'
                ).text.strip()
                issue_id = row.find_element(
                    By.CSS_SELECTOR, '[col-id="issue_id"] .ag-cell-value span'
                ).text.strip()

                # Append the extracted data to the table_data list
                table_data.append(
                    {
                        "path": path,
                        "severity": severity,
                        "applicability": applicability,
                        "issue_id": issue_id,
                    }
                )

            except StaleElementReferenceException:
                # Handle stale element by re-locating the rows and retrying
                log.warning(f"Stale element encountered for row {index}. Retrying...")
                rows = self.wait.until(EC.presence_of_all_elements_located(self.ROWS))
                row = rows[index]

        return table_data
