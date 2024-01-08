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
from dataclasses import dataclass, field, fields


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
    def get_cv_data(self, cv: WebElement) -> dict[str, dict]:
        pass


class WorkUaScraper(Scraper):

    def __init__(self: "WorkUaScraper", params: "WorkUaConfigParams") -> None:
        for f in fields(params):
            setattr(self, f.name, getattr(params, f.name))

    def load_cv(self: "WorkUaScraper", browser: webdriver.Chrome, single: bool) -> WebElement | list[WebElement]:
        if single:
            return WebDriverWait(browser, 10).until(
                ec.visibility_of_element_located((By.CSS_SELECTOR, self.cv_selector))
            )
        return WebDriverWait(browser, 10).until(
            ec.visibility_of_all_elements_located((By.CSS_SELECTOR, self.cv_preview_selector))
        )

    def get_cv_data(self: "WorkUaScraper", cv: WebElement) -> dict[str, dict]:
        cv_url = self.get_cv_url(cv)
        html = cv.get_attribute("innerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        name = self.get_name(soup)
        position = self.get_position(soup)
        experience = self.get_experience(soup)
        print(cv_url)
        print(name)
        print(position)
        for exp in experience:
            print(exp)
        return {cv_url: {
            "name": name,
            "position": position,
            "experience": experience
        }}

    def get_cv_url(self: "WorkUaScraper", cv: WebElement) -> str:
        cv_id = cv.get_attribute("id").split("_")[1]
        return self.cv_url_prefix + cv_id + "/"

    def get_name(self: "WorkUaScraper", soup: BeautifulSoup) -> str:
        name_element = soup.find(self.name_selector["tag"], class_=self.name_selector["class"])
        return name_element.text.strip()

    def get_position(self: "WorkUaScraper", soup: BeautifulSoup) -> str:
        position_element = soup.find(self.position_selector["tag"], class_=self.position_selector["class"])
        return position_element.text.strip()

    def get_experience(self: "WorkUaScraper", soup: BeautifulSoup) -> list[str]:
        experience_elements = soup.find_all(self.experience_selector["tag"], class_=self.experience_selector["class"],
                                            id=lambda x: x != self.experience_selector["exclude"])
        experience = []
        for exp_element in experience_elements:
            experience.append(exp_element.text.strip())
        return experience
