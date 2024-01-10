from src.models.work_ua_query_builder import WorkUaQueryParams


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
