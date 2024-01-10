from abc import abstractmethod
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.remote.webelement import WebElement


class Scraper:
    @abstractmethod
    def load_cv(self: "Scraper", browser: webdriver, single: bool) -> WebElement | list[WebElement]:
        pass

    @abstractmethod
    def get_cv_data(self: "Scraper", cv: WebElement) -> dict[str, dict]:
        pass
