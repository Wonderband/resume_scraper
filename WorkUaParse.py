from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
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
    position_selector: dict[str, str] = field(default_factory=lambda: {"tag": "h2", "class": "add-top-exception add-top-exception-xs"})
    experience_selector: dict[str, str] = field(default_factory=lambda: {"tag": "h2", "class": "h4 strong-600 add-top-exception add-top-exception-xs", "exclude": "contactInfo"})

    field(default_factory=lambda: {
        'line1': None,
        'line2': None,
        'etc': None,
    })


class ChromeDriver:
    def __init__(self):
        self.browser = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
        )
        self.tabs = None
        self.options = {
            "timeout": 30,
        }
        self.browser.set_page_load_timeout(self.options["timeout"])

    def request_site(self, query):
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


class GetElementsBySelector:
    def __init__(self, selector):
        self.selector = selector

    def load(self, browser, single):
        if single:
            return WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.selector))
            )
        return WebDriverWait(browser, 10).until(
            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, self.selector))
        )


class ScrapeElement:
    def __init__(self, element):
        self.element = element
        self.cv_url = None
        self.name = None
        self.position = None
        self.experience = None

    def get_data(self, params):
        html = self.element.get_attribute("innerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        self.get_cv_url(params.cv_url_prefix)
        self.get_name(soup, params.name_selector)
        self.get_position(soup, params.position_selector)
        self.get_experience(soup, params.experience_selector)
        print(self.cv_url)
        print(self.name)
        print(self.position)
        for exp in self.experience:
            print(exp)

    def get_cv_url(self, url_prefix):
        cv_id = self.element.get_attribute("id").split("_")[1]
        self.cv_url = url_prefix + cv_id + "/"

    def get_name(self, soup, name_selector):
        name_element = soup.find(name_selector["tag"], class_=name_selector["class"])
        self.name = name_element.text.strip()

    def get_position(self, soup, position_selector):
        position_element = soup.find(position_selector["tag"], class_=position_selector["class"])
        self.position = position_element.text.strip()

    def get_experience(self, soup, experience_selector):
        experience_elements = soup.find_all(experience_selector["tag"], class_=experience_selector["class"],
                                            id=lambda x: x != experience_selector["exclude"])
        experience = []
        for exp_element in experience_elements:
            experience.append(exp_element.text.strip())
        self.experience = experience
