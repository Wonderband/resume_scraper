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
class WorkUaQueryParams:
    url: str = "https://www.work.ua/resumes-"
    employment_full = 74
    employment_partial = 75
    age_from = 14
    age_to = 100
    photo = "photo=1"
    gender_male = 86
    gender_female = 87


@dataclass
class WorkUaConfigParams:
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
    add_info_selector: dict[str, str] = field(
        default_factory=lambda: {"tag": "div", "class": "wordwrap", "id": "add_info"})


class UserDialog:
    def __init__(self):
        self.input = {}

    def prompt_user(self):
        keyword = input("Enter the keyword for search: ")
        full_time_input = input("Are you looking for full-time employment? (y/n): ").lower()
        employment_full = WorkUaQueryParams().employment_full if full_time_input == "y" else ""
        partial_time_input = input("Are you looking for partial-time employment? (y/n): ").lower()
        employment_partial = WorkUaQueryParams().employment_partial if partial_time_input == "y" else ""
        age_from = input("Age from: ").lower()
        age_to = input("Age to: ").lower()
        photo_input = input("Do you need CV with photo? (y/n): ").lower()
        photo = WorkUaQueryParams().photo if photo_input == "y" else ""
        male_input = input("Do you consider males? (y/n): ").lower()
        gender_male = WorkUaQueryParams().gender_male if male_input == "y" else ""
        female_input = input("Do you consider females? (y/n): ").lower()
        gender_female = WorkUaQueryParams().gender_female if female_input == "y" else ""

        self.input = {
            "keyword": keyword,
            "employment_full": employment_full,
            "employment_partial": employment_partial,
            "age_from": age_from,
            "age_to": age_to,
            "photo": photo,
            "gender_male": gender_male,
            "gender_female": gender_female,

        }


class WorkUaQueryBuilder:
    def __init__(self, user_input):
        self.url = WorkUaQueryParams().url
        self.keyword = user_input["keyword"]
        self.employment = self.get_employment(user_input)
        self.age = self.get_age(user_input)
        self.gender = self.get_gender(user_input)
        self.photo = self.get_photo(user_input)

    @staticmethod
    def get_employment(user_input):
        if not (user_input["employment_full"] or user_input["employment_partial"]):
            return ""
        query = f"{user_input['employment_full']}+{user_input['employment_partial']}"
        if query.startswith("+") or query.endswith("+"):
            query = query.replace("+", "")
        return f"employment={query}"

    @staticmethod
    def get_age(user_input):
        if not (user_input["age_from"] or user_input["age_to"]):
            return ""
        query = f"agefrom={user_input['age_from']}&ageto={user_input['age_to']}"
        if query.endswith("="):
            query = query.removesuffix("&ageto=")
        if query.startswith("agefrom=&"):
            query = query.removeprefix("agefrom=")
        return query

    @staticmethod
    def get_photo(user_input):
        return user_input["photo"]

    @staticmethod
    def get_gender(user_input):
        if not (user_input["gender_male"] or user_input["gender_female"]):
            return ""
        query = f"{user_input['gender_male']}+{user_input['gender_female']}"
        if query.startswith("+") or query.endswith("+"):
            query = query.replace("+", "")
        return f"gender={query}"

    def create_query(self):
        if not self.keyword:
            self.url = self.url.removesuffix("-")
        query = self.url + self.keyword + "/"
        filters = "&".join([self.employment, self.age, self.gender, self.photo])
        while "&&" in filters:
            filters = filters.replace("&&", "")
        if not filters:
            return query
        filters = filters.strip("&")
        query = query + "?" + filters
        return query


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
            # "add_info": self.get_add_info(soup, params)
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

    @staticmethod
    def get_add_info(soup: BeautifulSoup, params: WorkUaConfigParams) -> str:
        add_info_element = soup.find(params.add_info_selector["tag"], class_=params.add_info_selector["class"],
                                     id=params.add_info_selector["id"])
        return add_info_element.text.strip().replace("\xa0", " ")
