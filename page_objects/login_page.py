"""
This module defines the `LoginPage` class, which represents the
 login page 
of the JFrog Artifactory web interface.

Purpose:
- To provide locators and methods for interacting with elements on
 the login page.

Dependencies:
- Selenium WebDriver: Used for locating and interacting with web elements.
- PageObject: A base class that provides common functionality
 for page objects.

Note:
- Ensure that the Selenium WebDriver is properly initialized
 before using this class.
- The locators and methods are specific to the JFrog Artifactory login page.
Author: Shwetha Kamath
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from page_objects.page_objects import PageObject


class LoginPage(PageObject):
    """
    This class Represents the login page of the JFrog Artifactory
      web interface.

    This class provides locators and methods to interact with elements
      on the login page,
    """

    USERNAME_INPUT = (By.NAME, "username")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")

    def login(self, username, password):
        """
        Log in to the application using the provided username and password.

        This method enters the username and password into their
          respective fields,
        takes a screenshot of the login page, and clicks the login button.

        Args:
            username (str): The username to log in with.
            password (str): The password to log in with.
        """
        self.enter_text(self.USERNAME_INPUT, username)
        self.enter_text(self.PASSWORD_INPUT, password)
        self.take_screenshot("Login_page.png")
        self.click_element(self.LOGIN_BUTTON)

    def open_page(self):
        """
        Open the login page.

        This method navigates to the login page using the WebDriver.
        """
        self.open_page()

    def enter_username(self, password):
        """
        Enter the username into the username input field.

        Args:
            username (str): The username to enter.
        """
        self.send_password(element="i0118", password=password)

    def click_on_login_button(self):
        """
        Click the login button.

        This method clicks the login button to submit the login form.
        """
        self.click(self.login_button)
