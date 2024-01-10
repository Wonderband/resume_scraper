from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains


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
