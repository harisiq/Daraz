"""
Daraz Scraper Module

This module contains a class `DarazScraper` that is used to scrape product information 
from Daraz (name, price, sold count) across multiple pages and save the data to a CSV file. 
It uses Selenium WebDriver to automate browser interactions, and Loguru for logging.

Classes:
    DarazScraper: Scrapes product data from Daraz website and writes it to a CSV file.

Usage:
    python daraz_scraper.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import csv
from loguru import logger
from constants import Xpaths

class DarazScraper:
    """
    A class to represent the Daraz product scraper.

    Attributes:
        url (str): The URL of the Daraz page to scrape.
        csv_file (str): The path to the CSV file where the scraped data will be saved.
    
    Methods:
        start_driver(): Launches the Chrome WebDriver and navigates to the provided URL.
        scrape_products(): Scrapes product data (name, price, sold) from the current page.
        go_to_next_page(): Navigates to the next page of product listings.
        scrape_all_pages(pages=5): Scrapes product data from the specified number of pages.
        write_to_csv(data): Writes the scraped product data to a CSV file.
        quit_driver(): Closes the WebDriver instance gracefully.
    """
    
    def __init__(self, url: str, csv_file: str):
        """
        Initializes the DarazScraper with the URL to scrape and the CSV file for saving data.
        """
        self.driver = webdriver.Chrome()
        self.url = url
        self.csv_file = csv_file
        logger.add("daraz_scraper.log", rotation="1 MB", level="INFO")  # Setup rotating log file

    def start_driver(self):
        """
        Launches the Chrome WebDriver and navigates to the specified URL.

        This method waits 2 seconds after page load to ensure that all elements are loaded.
        """
        logger.info(f"Opening URL: {self.url}")
        try:
            self.driver.get(self.url)
            time.sleep(2)  # Allow page to load
        except Exception as e:
            logger.error(f"Failed to open the URL: {e}")
            self.quit_driver()

    def scrape_products(self):
        """
        Scrapes product details (name, price, sold) from the current page and saves them to CSV.

        The method uses XPath from the `constants.py` file to locate product details.
        Handles NoSuchElementException when product details are missing.
        """
        product_data = []
        try:
            product_containers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, Xpaths.PRODUCT_CONTAINER.value))
            )
            logger.info(f"Found {len(product_containers)} products on the page")

            for container in product_containers:
                try:
                    product_name = container.find_element(By.XPATH, Xpaths.PRODUCT_NAME.value).text
                    product_price = container.find_element(By.XPATH, Xpaths.PRODUCT_PRICE.value).text
                    product_sold = container.find_element(By.XPATH, Xpaths.PRODUCT_SOLD.value).text
                    product_data.append([product_name, product_price, product_sold])
                except NoSuchElementException as e:
                    logger.error(f"Product details not found in container: {e}")

            self.write_to_csv(product_data)

        except TimeoutException:
            logger.error("Timed out while waiting for product containers")
        except Exception as e:
            logger.error(f"Error scraping products: {e}")

    def go_to_next_page(self):
        """
        Navigates to the next page of products.

        This method waits for the next page button to become clickable and waits 3 seconds 
        after clicking to allow the page to load completely.
        """
        try:
            next_page_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, Xpaths.NEXT_PAGE.value))
            )
            next_page_button.click()
            logger.info("Navigated to the next page")
            time.sleep(3)  # Delay for page load
        except TimeoutException:
            logger.warning("Next page button not found or not clickable")
        except Exception as e:
            logger.error(f"Error navigating to the next page: {e}")

    def write_to_csv(self, data):
        """
        Writes the scraped product data to the specified CSV file.

        Args:
            data (list): List of product details, where each item is a list containing 
            the product name, price, and sold count.
        """
        try:
            with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)
                logger.info(f"{len(data)} records written to CSV")
        except Exception as e:
            logger.error(f"Error writing data to CSV: {e}")

    def scrape_all_pages(self, pages: int = 5):
        """
        Scrapes multiple pages of product data from Daraz and writes them to a CSV file.

        Args:
            pages (int): The number of pages to scrape. Defaults to 5 pages.
        """
        self.start_driver()

        for page in range(pages):
            try:
                logger.info(f"Scraping page {page + 1}/{pages}")
                self.scrape_products()
                
                if page < pages - 1:  # Avoid going to the next page on the last iteration
                    self.go_to_next_page()
            except Exception as e:
                logger.error(f"Error scraping page {page + 1}: {e}")
                break

        self.quit_driver()

    def quit_driver(self):
        """
        Quits the Chrome WebDriver gracefully.

        Ensures that the WebDriver instance is closed, even in case of errors.
        """
        try:
            self.driver.quit()
            logger.info("Web driver closed successfully")
        except Exception as e:
            logger.error(f"Error closing the WebDriver: {e}")


if __name__ == "__main__":
    url = 'https://www.daraz.pk/catalog/?spm=a2a0e.tm80335142.search.d_go&q=mobile'  # Example URL
    csv_file = 'daraz_products.csv'

    scraper = DarazScraper(url, csv_file)
    scraper.scrape_all_pages(pages=5)
