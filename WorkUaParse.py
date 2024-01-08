from abc import abstractmethod
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from dataclasses import dataclass, field


@dataclass
class WorkUaConfigParams:
    url: str = "https://www.work.ua/resumes-"
    keyword: str = "developer"
    query: str = f"{url}{keyword}/"
    cv_preview_selector: str = "div.card-search.resume-link.card-visited.wordwrap"
    cv_selector: str = "div.card.wordwrap.cut-top"
    cv_id_prefix: str = "resume_"
    cv_url_prefix: str = "https://www.work.ua/resumes/"
    name_selector: dict[str, str] = field(default_factory=lambda: {"tag": "h1", "class": "cut-top"})
    position_selector: dict[str, str] = field(
        default_factory=lambda: {"tag": "h2", "class": "add-top-exception add-top-exception-xs"})
    experience_selector: dict[str, str] = field(
        default_factory=lambda: {"tag": "h2", "class": "h4 strong-600 add-top-exception add-top-exception-xs",
                                 "exclude": "contactInfo"})
    date_selector: dict[str, str] = field(
        default_factory=lambda: {"tag": "span", "class": "text-default-7 add-right-xs add-bottom-sm"})
    details_selector: dict[str, str] = field(
        default_factory=lambda: {"tag": "dl", "class": "dl-horizontal"})


class ChromeDriver:
    def __init__(self: "ChromeDriver") -> None:
        self.browser = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
        )
        self.tabs = None
        self.options = {
            "timeout": 30,
        }
        self.browser.set_page_load_timeout(self.options["timeout"])

    def request_site(self: "ChromeDriver", query: str) -> webdriver.Chrome:
        self.browser.get(query)
        return self.browser

    def open_new_tab(self, element_to_click):
        actions = ActionChains(self.browser)
        actions.key_down(Keys.CONTROL)
        actions.click(on_element=element_to_click)
        actions.perform()

    def switch_to_new_tab(self):
        self.tabs = self.browser.window_handles
        self.browser.switch_to.window(self.tabs[1])

    def back_to_main(self):
        self.browser.close()
        self.browser.switch_to.window(self.tabs[0])

    def quit(self):
        self.browser.quit()


class Scraper:
    @abstractmethod
    def load_cv(self: "Scraper", browser: webdriver.Chrome, single: bool) -> WebElement | list[WebElement]:
        pass

    @abstractmethod
    def get_cv_data(self: "Scraper", cv: WebElement) -> dict[str, dict]:
        pass


class WorkUaScraper(Scraper):
    def __init__(self: "WorkUaScraper") -> None:
        self.params = WorkUaConfigParams()

    def load_cv(self: "WorkUaScraper", browser: webdriver.Chrome, single: bool) -> WebElement | list[WebElement]:
        params = self.params
        if single:
            return WebDriverWait(browser, 10).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, params.cv_selector))
            )
        return WebDriverWait(browser, 10).until(
            ec.visibility_of_all_elements_located((By.CSS_SELECTOR, params.cv_preview_selector))
        )

    def get_cv_data(self: "WorkUaScraper", cv: WebElement) -> dict[str, dict]:
        params = self.params
        cv_url = self.get_cv_url(cv, params)
        html = cv.get_attribute("innerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        details = self.get_details(soup, params)
        title = self.get_title(soup, params)
        cv_data = {
            "date": self.get_date(soup, params),
            "name": self.get_name(soup, params),
            "position": self.get_position(title),
            "salary": self.get_salary(title),
            "experience": self.get_experience(soup, params),
            "employment": self.get_employment(details),
            "age": self.get_age(details),
            "city": self.get_city(details),
            "places": self.get_places(details),
        }
        for key, value in cv_data.items():
            if value:
                print(f"{key}: {value}")
        return {cv_url: cv_data}

    @staticmethod
    def get_cv_url(cv: WebElement, params: WorkUaConfigParams) -> str:
        cv_id = cv.get_attribute("id").split("_")[1]
        return params.cv_url_prefix + cv_id + "/"

    @staticmethod
    def get_name(soup: BeautifulSoup, params: WorkUaConfigParams) -> str:
        name_element = soup.find(params.name_selector["tag"], class_=params.name_selector["class"])
        return name_element.text.strip()

    @staticmethod
    def get_title(soup: BeautifulSoup, params: WorkUaConfigParams) -> str:
        title_element = soup.find(params.position_selector["tag"], class_=params.position_selector["class"])
        return title_element.text.strip().replace("\xa0", " ")

    @staticmethod
    def get_position(title: str) -> str:
        if "грн" not in title:
            return title
        return ",".join(title.split(",")[:-1]).replace("\xa0", " ").strip()

    @staticmethod
    def get_salary(title: str) -> int:
        if "грн" not in title:
            return 0
        return int(title.split(",")[-1].removesuffix("грн").replace(" ", "").strip())

    @staticmethod
    def get_experience(soup: BeautifulSoup, params: WorkUaConfigParams) -> list[str]:
        experience_elements = soup.find_all(params.experience_selector["tag"],
                                            class_=params.experience_selector["class"],
                                            id=lambda x: x != params.experience_selector["exclude"])
        experience = []
        for exp_element in experience_elements:
            experience.append(exp_element.text.strip())
        return experience

    @staticmethod
    def get_date(soup: BeautifulSoup, params: WorkUaConfigParams) -> str:
        date_element = soup.find(params.date_selector["tag"], class_=params.date_selector["class"])
        return date_element.text.replace("\xa0", " ").removeprefix("Резюме від").strip()

    @staticmethod
    def get_details(soup: BeautifulSoup, params: WorkUaConfigParams) -> dict["str", "str"]:
        details_wrapper = soup.find(params.details_selector["tag"], class_=params.details_selector["class"])
        key_elements = details_wrapper.select('dt')
        details = {}
        for key_element in key_elements:
            key = key_element.get_text(strip=True).replace("\xa0", " ").removesuffix(':')
            value_element = key_element.find_next('dd')
            value = value_element.get_text(strip=True).replace("\xa0", " ")
            details[key] = value
        return details

    @staticmethod
    def get_employment(details: dict["str", "str"]) -> str | None:
        return details["Зайнятість"] if "Зайнятість" in details.keys() else None

    @staticmethod
    def get_age(details: dict["str", "str"]) -> int | None:
        return int(details["Вік"].split()[0]) if "Вік" in details.keys() else None

    @staticmethod
    def get_city(details: dict["str", "str"]) -> str | None:
        if "Місто" in details.keys():
            return details["Місто"]
        if "Місто проживання" in details.keys():
            return details["Місто проживання"]
        return None

    @staticmethod
    def get_places(details: dict["str", "str"]) -> str | None:
        return details["Готовий працювати"] if "Готовий працювати" in details.keys() else None
