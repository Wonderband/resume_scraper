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


class WorkUaParseParams:
    def __init__(self):
        self.url = "https://www.work.ua/resumes-"
        self.keyword = "developer"
        self.query = self.url + self.keyword + "/"
        self.cv_preview_selector = "div.card-search.resume-link.card-visited.wordwrap"
        self.cv_selector = "div.card.wordwrap.cut-top"
        self.cv_id_prefix = "resume_"
        self.cv_url_prefix = "https://www.work.ua/resumes/"
        self.name_selector = {"tag": "h1", "class": "cut-top"}
        self.position_selector = {"tag": "h2", "class": "add-top-exception add-top-exception-xs"}
        self.experience_selector = {"tag": "h2", "class": "h4 strong-600 add-top-exception add-top-exception-xs",
                                    "exclude": "contactInfo"}


class ChromeDriver:
    def __init__(self):
        self.browser = None
        self.tabs = None
        self.options = {
            "timeout": 30,
        }

    def start(self):
        self.browser = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),

        )
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

# class ClickElements:
#     def __init__(self, elements, driver, click):
#         self.elements = elements
#         self.driver = driver
#         self.click = click
#
#     def
#         for cv_preview in cv_previews:
#             click.open_new_tab(cv_preview)
#             driver.switch_to_new_tab()
#             cv = GetElementsBySelector(params.cv_selector).load(browser, True)
#             cv_html = cv.get_attribute("innerHTML")
#             print(cv_html[:200])
#             driver.back_to_main()
# r = requests.get('https://api.github.com/events')
# json_content = r.json()
# formatted_json = json.dumps(json_content, indent=2)
# print(formatted_json)

# url = 'https://robota.ua/candidates/developer/ukraine'
# response = requests.get(url)
#
# print(response.status_code)
# print(response.headers)
# print(response.text)
#
# print("--------------ROBOTA---------------------------")

# url = 'https://www.work.ua/resumes/9520350/'
# response = requests.get(url)
#
# print(response.status_code)
# print(response.headers)
# print(response.text)


# url = 'https://www.work.ua/resumes-developer/'


# Use a web driver (make sure to have the appropriate driver installed, e.g., chromedriver)

# def init_driver() -> webdriver.Chrome:
#     driver = webdriver.Chrome(
#         service=ChromeService(ChromeDriverManager().install()),
#
#     )
#     driver.set_page_load_timeout(30)
#     return driver


# driver = init_driver()
# driver.get(url)

# Wait until the <p> element is visible
# element_xpath = "//p[@class='santa-mt-0 santa-mb-10 santa-typo-regular santa-text-black-700 ng-star-inserted']"
# wait = WebDriverWait(driver, 50)
# element = wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))

# Wait for the div elements to be present and visible
# div_elements = WebDriverWait(driver, 10).until(
#     EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.card-search.resume-link.card-visited.wordwrap"))
# )
# print(div_elements)
# actions = ActionChains(driver)
# resume_selector = "div.card.wordwrap.cut-top"
# original_window = driver.current_window_handle
# for div_element in div_elements:
#     actions.key_down(Keys.CONTROL)
#     actions.click(on_element=div_element)
#     actions.perform()
#     tabs = driver.window_handles
#     driver.switch_to.window(tabs[1])
#     resume = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, resume_selector)))
#     resume_html = resume.get_attribute("innerHTML")
#     soup = BeautifulSoup(resume_html, 'html.parser')
#     name = soup.find('h1', class_='cut-top')
#     position = soup.find('h2', class_='add-top-exception add-top-exception-xs')
#     experience = soup.find_all('h2', class_='h4 strong-600 add-top-exception add-top-exception-xs',
#                                id=lambda x: x != 'contactInfo')
#     experience_text = []
#     for exp in experience:
#         experience_text.append(exp.text)
#     name_text = name.text
#     position_text = position.text
#     print(name_text.strip())
#     print(position_text.strip())
#     for exp in experience_text:
#         print(exp)
#     driver.close()
#     driver.switch_to.window(tabs[0])

# div_elements[0].click()

# driver.execute_script("window.history.go(-1)")
# print(div_elements)
# div_elements[1].click()
# sleep(10)
# driver.execute_script("window.history.go(-1)")
# sleep(10)

# driver.quit()
# Iterate through each div element
# for index, div_element in enumerate(div_elements):
#     try:
#         # Click the div element to open a new page
#         div_element.click()
#
#         # Perform actions on the opened page (e.g., scraping content)
#         # You can use driver.page_source to get the HTML content of the current page
#         opened_page_content = driver.page_source
#         # Add your scraping logic here
#
#         # Go back to the initial page (assuming each div click opens a new page)
#         driver.execute_script("window.history.go(-1)")
#
#         # Refresh the list of div elements to avoid StaleElementReferenceException
#         div_elements = WebDriverWait.until(
#             EC.visibility_of_all_elements_located((By.CLASS_NAME, "card-search"))
#         )
#
#     except Exception:
#         # Handle StaleElementReferenceException by refreshing the list of elements
#         print(f"Element at index {index} became stale. Refreshing the list.")
#
#
# # # Get the HTML content after waiting
# # html_content = driver.page_source
# # Close the browser
# driver.quit()
# #
# # # Now you can print or process the HTML content
# print(scraped_data)
