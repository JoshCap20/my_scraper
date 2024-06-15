import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, ReadTimeout, RequestException
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class Scraper:
    """
    A web scraper class that supports retry logic, proxy usage, and custom headers.

    Attributes:
        url (str): The URL to scrape.
        timeout (int): Timeout for the requests.
        retries (int): Number of retry attempts.
        proxy (str | None): Proxy server URL.
        headers (dict[str, str] | None): HTTP headers for the requests.
        data (BeautifulSoup | None): The parsed HTML data.
        cleaned_data (str): The cleaned and formatted HTML data.

    Methods:
        scrape(): Performs the web scraping operation.
    """

    def __init__(
        self,
        url: str,
        timeout: int = 15,
        retries: int = 5,
        proxy: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        """
        Initializes the Scraper with a URL, optional headers, timeout, and proxy.

        :param url: URL to scrape.
        :param timeout: Request timeout in seconds.
        :param retries: Number of retries for the request.
        :param proxy: Optional proxy server.
        :param headers: Optional headers for the request.
        """
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.retries = retries
        self.proxy = proxy
        self.data = None
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Creates a requests session with retry logic.

        :return: Configured requests session.
        """
        session = requests.Session()
        retries = Retry(
            total=self.retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        return session

    def scrape(self) -> None:
        """
        Performs the web scraping operation.

        :raises ValueError: If the URL is not set.
        :raises ConnectionError: If a network error occurs.
        :raises ReadTimeout: If the request times out.
        :raises RequestException: If an error occurs during the request.
        """
        if self.session is None:
            raise ValueError("Session is not set")
        if self.url is None:
            raise ValueError("URL is not set")
        if self.data is not None:
            logger.info("Clearing existing data")
            self.data = None

        try:
            logger.info(f"Scraping {self.url}")
            response = self.session.get(
                url=self.url, headers=self.headers, timeout=(5, self.timeout)
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            self.data = soup
            logger.info("Scraping successful")
        except (ConnectionError, ReadTimeout) as e:
            logger.error(f"Network error or timeout: {e}")
        except RequestException as e:
            logger.error(f"Error during requests to {self.url}: {e}")

    ##########################################################################################
    # Property Getters and Setters

    @property
    def proxy(self) -> str | None:
        return self._proxy

    @proxy.setter
    def proxy(self, proxy: str | None):
        """
        Sets the proxy for the scraper.

        :param proxy: The proxy to be set. If None, the proxy will be cleared.
        :raises ValueError: If the proxy is not a string.
        """
        if proxy is not None and not isinstance(proxy, str):
            raise ValueError("Proxy must be a string")
        self._proxy = proxy

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, headers: dict[str, str] | None):
        """
        Sets the headers for the scraper.

        :param headers: The headers to be set. If None, default headers will be used.
        """
        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
        self._headers = headers

    @property
    def data(self) -> BeautifulSoup:
        return self._data

    @data.setter
    def data(self, data: BeautifulSoup | None):
        """
        Sets the data for the scraper.

        :param data: The data to be set. If None, the data will be cleared.
        """
        self._data = data

    @property
    def cleaned_data(self) -> str:
        """
        Returns the cleaned and formatted HTML data.

        :return: The cleaned and formatted HTML data.
        """
        return self.data.prettify() if self.data else ""

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str):
        """
        Sets the URL for the scraper.

        :param url: The URL to be set.
        :raises ValueError: If the URL is None or not a string.
        :raises ValueError: If the URL does not start with http or https.
        """
        if not url:
            raise ValueError("URL cannot be None")
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        if not url.startswith("http"):
            raise ValueError("URL must start with http or https")
        self._url = url


if __name__ == "__main__":
    # Example usage
    url = "https://www.example.com"
    scraper = Scraper(url)
    scraper.scrape()
    if scraper.data:
        print(scraper.cleaned_data)
