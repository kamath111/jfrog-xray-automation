"""
This module defines the 'PageObject' class, which serves as a base class
for all page objects  in the JFrog Artifactory web interface 
automation framework.

Purpose:
- To provide common functionality for interacting with web elements
 across different pages.
- To encapsulate reusable methods such as finding elements, 
clicking elements, entering text, 
  taking screenshots, and interacting with tables.

Features:
- Wait for elements to be visible or present.
- Click elements using standard or JavaScript-based methods.
- Enter text into input fields.
- Capture screenshots for debugging or verification purposes.
- Retrieve rows and columns from HTML tables.

Dependencies:
- Selenium WebDriver: Used for locating and interacting with web elements.

Note:
- Ensure that the Selenium WebDriver is properly initialized
 before using this class.
- This class is intended to be inherited by specific page object classes.
Author: Shwetha Kamath
"""

import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util import logging

# Logging is by default set to WARNING
# Enable it for INFO/DEBUG to have proper log messages
log = logging.get_main_logger()
log.setLevel("INFO")
logging.addStreamHandler("INFO")


class PageObject:
    """
    Base class for all page objects in the JFrog Artifactory automation
      framework.

    This class provides common methods for interacting with web elements,
    such as finding elements, clicking elements, entering text,
    and taking screenshots.

    Attributes:
        driver (WebDriver): The Selenium WebDriver instance used
          for interacting with the browser.
        wait (WebDriverWait): A WebDriverWait instance for waiting
          for elements to be present or visible.
        screenshot_dir (str): The directory where screenshots will be saved.
    """

    def __init__(self, driver, screenshot_dir):
        """
        Initialize the PageObject with a WebDriver instance
          and a screenshot directory.

        Args:
            driver (WebDriver): The Selenium WebDriver instance.
            screenshot_dir (str): The directory where screenshots
              will be saved.
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 60)
        self.screenshot_dir = screenshot_dir

    def open_page(self):
        """
        Open the page using the URL defined in the child class.

        This method navigates to the page URL and logs the page title.
        """
        self.driver.get(self.url)
        log.info(self.driver.title)

    def take_screenshot(self, file_name):
        """
        Capture a screenshot of the current page.

        Args:
            file_name (str): The name of the screenshot file.
        """
        screenshot_path = os.path.join(self.screenshot_dir, file_name)
        time.sleep(5)
        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at: {screenshot_path}")

    def find_element(self, element="", xpath=""):
        """
        Find a web element

        Args:
            element (str, optional): The ID of the element to find
            xpath (str, optional): The XPath of the element to find

        Returns:
            WebElement: The located web element.

        Raises:
            Exception: If the element cannot be found.
        """
        self.element = element
        self.xpath = xpath
        element_obj = ""
        try:
            if self.element:
                log.info(f"Find the element by id {self.element}")
                self.wait.until(EC.visibility_of_element_located((By.ID, self.element)))
                element_obj = self.driver.find_element(By.ID, self.element)
            elif xpath:
                log.info(f"Find the element by xpath {self.xpath}")
                self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
                element_obj = self.driver.find_element(By.XPATH, xpath)
            else:
                raise Exception
        except Exception as err:
            log.info(f"Element not available. Searching through xpath.{err}")
            element_obj = self.driver.find_element(By.XPATH, xpath)
        finally:
            return element_obj

    def find_text(self, text=""):
        """
        Check if the specified text is present on the page.

        Args:
            text (str): The text to search for.

        Returns:
            bool: True if the text is found, False otherwise.
        """
        return text in self.driver.page_source

    def get_all_table_rows(self, table_id):
        """
        Retrieve all rows from an HTML table.

        Args:
            table_id (WebElement): The table element.

        Returns:
            list: A list of row elements.
        """
        rows = []
        try:
            rows = table_id.find_elements(By.TAG_NAME, "tr")
        except Exception as err:
            log.info(f"Error occurred: {err}")
        finally:
            return rows

    def get_all_row_columns(self, row_id):
        """
        Retrieve all columns (headers and data) from a table row.

        Args:
            row_id (WebElement): The row element.

        Returns:
            tuple: A tuple containing a list of header elements
              and a list of data elements.
        """
        headers = []
        try:
            headers = row_id.find_elements(By.TAG_NAME, "th")
        except Exception as err:
            log.info(f"Error occurred in headers of the table: {err}")
        datas = []
        try:
            datas = row_id.find_elements(By.TAG_NAME, "td")
        except Exception as err:
            log.info(f"Error occurred the rows of the table: {err}")
        finally:
            return headers, datas

    def wait_for_element(self, locator):
        """
        Wait for an element to be present on the page.

        Args:
            locator (tuple): The locator of the element.

        Returns:
            WebElement: The located web element.
        """
        return self.wait.until(EC.presence_of_element_located(locator))

    def click_element(self, locator):
        """
        Click on a web element.

        Args:
            locator (tuple): The locator of the element to click.
        """
        element = self.wait_for_element(locator)
        element.click()
        log.info(f"Page Title: {self.driver.title}")
        log.info(f"Clicked on element: {locator}")

    def click_element_javascript(self, locator):
        """
        Click on a web element using JavaScript.

        Args:
            locator (tuple): The locator of the element to click.
        """
        svg_element = self.wait_for_element(locator)
        self.driver.execute_script(
            """
        var evt = new MouseEvent('click', {
        bubbles: true,
        cancelable: true,
        view: window
        });
        arguments[0].dispatchEvent(evt);
        """,
            svg_element,
        )
        log.info(f"Clicked on the element: {svg_element}")

    def enter_text(self, locator, text):
        """
        Enter text into an input field.

        Args:
            locator (tuple): The locator of the input field.
            text (str): The text to enter.
        """
        element = self.wait_for_element(locator)
        element.send_keys(text)
