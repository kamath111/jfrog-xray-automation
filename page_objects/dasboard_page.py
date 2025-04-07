"""
This module defines the 'DashboardPage' class, which represents the
 Dashboard page 
in the JFrog Artifactory web interface.

Purpose:
- To provide locators and methods for interacting with elements
 on the Dashboard page.

 Dependencies:
- Selenium WebDriver: Used for locating and interacting with web elements.
- PageObject: A base class that provides common functionality
 for page objects.

Note:
- Ensure that the Selenium WebDriver is properly
 initialized before using this class.
- The locators and methods are specific to the JFrog
 Artifactory Dashboard page.
Author: Shwetha Kamath
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_objects.page_objects import PageObject


class DashboardPage(PageObject):
    """
    Represents the Dashboard page in the JFrog Artifactory web interface.

    This class provides locators and methods to interact with
      elements on the Dashboard page,
    such as navigating to the Xray section and
    selecting a specific repository.
    """

    XRAY_BUTTON = (By.XPATH, "//span[@class='vsm--title' and text()='Xray']")
    REPO_NAME = lambda self, repo_name: (By.XPATH, f"//span[text()='{repo_name}']")

    def navigate_to_xray(self):
        """
        Navigate to the Xray section of the Dashboard.

        This method clicks on the Xray button and waits for 2 seconds
          to ensure the page loads.
        It also takes a screenshot of the Xray section for verification.

        Raises:
            Exception: If the Xray button cannot be clicked.
        """
        self.click_element(self.XRAY_BUTTON)
        time.sleep(2)
        self.take_screenshot("dashboard_xray.png")

    def select_repository(self, repo_name):
        """
        Select a repository by its name.

        This method clicks on the repository name and takes
          a screenshot of the repository page.

        Args:
            repo_name (str): The name of the repository to select.

        Raises:
        Exception: If the repository cannot be found or clicked.
        """
        self.click_element(self.REPO_NAME(repo_name))
        self.take_screenshot(f"repository_{repo_name}.png")
