import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dynamic_scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

class DynamicScraper:
    """
    A web scraper class that uses Selenium to handle dynamic content.
    
    Attributes:
        url (str): The URL to scrape.
        timeout (int): Timeout for the requests.
        driver_path (str): Path to the WebDriver executable.
        options (webdriver.ChromeOptions): Selenium Chrome options.
        data (str | None): The page source HTML data.
    
    Methods:
        scrape(): Performs the web scraping operation.
    """
    
    def __init__(
        self,
        url: str,
        timeout: int = 15,
        options: Options | None = None,
        headers: dict[str, str] | None = None,
        rate_limit: int = 1
    ):
        """
        Initializes the DynamicScraper with a URL, timeout, and options.
        
        :param url: URL to scrape.
        :param timeout: Request timeout in seconds.
        :param options: Selenium Chrome options.
        :param headers: Optional headers for the request.
        :param rate_limit: Rate limit in seconds between requests.
        """
        self.url = url
        self.timeout = timeout
        self.headers = headers
        self.rate_limit = rate_limit
        self.options = options if options else self._default_options()
        self.data = None

    def _default_options(self) -> Options:
        """
        Creates default Selenium Chrome options.
        
        :return: Configured Chrome options.
        """
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if self.headers:
            for header, value in self.headers.items():
                options.add_argument(f"--header-{header}={value}")
        return options
    
    def _create_driver(self) -> webdriver.Chrome:
        """
        Creates a Selenium WebDriver instance.
        
        :return: Configured WebDriver instance.
        """
        try:
            service = Service()
            driver = webdriver.Chrome(service=service, options=self.options)
            return driver
        except WebDriverException as e:
            logger.error(f"Error creating WebDriver: {e}")
            raise

    def scrape(self) -> None:
        """
        Performs the web scraping operation.
        
        :raises ValueError: If the URL is not set.
        :raises TimeoutException: If the request times out.
        :raises WebDriverException: If an error occurs with the WebDriver.
        """
        if not self.url:
            raise ValueError("URL is not set")
        
        driver = self._create_driver()
        
        try:
            logger.info(f"Scraping {self.url}")
            driver.get(self.url)
            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.data = driver.page_source
            logger.info("Scraping successful")
        except TimeoutException as e:
            logger.error(f"Timeout while loading page: {e}")
        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
        finally:
            logger.info("Closing WebDriver")
            driver.quit()

    ##########################################################################################
    # Property Getters and Setters

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str):
        if not url:
            raise ValueError("URL cannot be None")
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        if not url.startswith("http"):
            raise ValueError("URL must start with http or https")
        self._url = url

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, headers: dict[str, str] | None):
        self._headers = headers

    @property
    def data(self) -> str:
        return self._data if self._data else ""

    @data.setter
    def data(self, data: str | None):
        self._data = data


if __name__ == "__main__":
    # Example usage
    url = "https://example.com"
    scraper = DynamicScraper(url)
    scraper.scrape()
    if scraper.data:
        print(scraper.data)
