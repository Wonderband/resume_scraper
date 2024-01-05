from WorkUaParse import ChromeDriver, WorkUaConfigParams, GetElementsBySelector, ScrapeElement


def main():
    params = WorkUaConfigParams()
    driver = ChromeDriver()
    browser = driver.request_site(params.query)
    cv_previews = GetElementsBySelector(params.cv_preview_selector).load(browser, False)
    for cv_preview in cv_previews:
        driver.open_new_tab(cv_preview)
        driver.switch_to_new_tab()
        cv = GetElementsBySelector(params.cv_selector).load(browser, True)
        ScrapeElement(cv).get_data(params)
        driver.back_to_main()
    driver.quit()


if __name__ == "__main__":
    main()
