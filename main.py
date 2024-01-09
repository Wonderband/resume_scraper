from WorkUaParse import ChromeDriver, WorkUaScraper, WorkUaQueryBuilder, UserDialog


def main() -> None:
    user_dialog = UserDialog()
    user_dialog.prompt_user()
    query = WorkUaQueryBuilder(user_dialog.input).create_query()
    print(query)
    scraper = WorkUaScraper()
    driver = ChromeDriver()
    browser = driver.request_site(query)
    cv_previews = scraper.load_cv(browser, False)
    for cv_preview in cv_previews:
        driver.open_new_tab(cv_preview)
        driver.switch_to_new_tab()
        cv = scraper.load_cv(browser, True)
        cv_data = scraper.get_cv_data(cv)
        print(cv_data)
        driver.back_to_main()
    driver.quit()


if __name__ == "__main__":
    main()
