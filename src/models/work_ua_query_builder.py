from src.models.work_ua_config import WorkUaQueryParams
from src.utils.helper_functions import get_code_from_sum, get_code_from_years


class WorkUaQueryBuilder:
    def __init__(self, user_input):
        self.url = WorkUaQueryParams().url
        self.keyword = user_input["keyword"]
        self.employment = self.get_employment(user_input)
        self.age = self.get_age(user_input)
        self.gender = self.get_gender(user_input)
        self.photo = self.get_photo(user_input)
        self.salary = self.get_salary(user_input)
        self.education = self.get_education(user_input)
        self.experience = self.get_experience(user_input)
        self.english = self.get_english(user_input)

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

    @staticmethod
    def get_salary(user_input):
        if not (user_input["salary_from"] or user_input["salary_to"]):
            return ""
        salary_from = get_code_from_sum(user_input["salary_from"])
        salary_to = get_code_from_sum(user_input["salary_to"])
        if not salary_from:
            return f"salaryto={salary_to}"
        if not salary_to:
            return f"salaryfrom={salary_from}"
        return f"salaryfrom={salary_from}&salaryto={salary_to}"

    @staticmethod
    def get_education(user_input):
        if not user_input["education"]:
            return ""
        return f"education={user_input['education']}"

    @staticmethod
    def get_experience(user_input):
        if not user_input["experience"]:
            return ""
        years = get_code_from_years(user_input["experience"])
        return f"experience={years}"

    @staticmethod
    def get_english(user_input):
        if not user_input["english"]:
            return ""
        return f"language={user_input['english']}"

    def create_query(self):
        if not self.keyword:
            self.url = self.url.removesuffix("-")
        query = self.url + self.keyword + "/"
        filters = "&".join(
            [
                self.employment,
                self.age,
                self.gender,
                self.photo,
                self.salary,
                self.education,
                self.experience,
                self.english,
            ]
        )
        while "&&" in filters:
            filters = filters.replace("&&", "&")
        if not filters:
            return query
        filters = filters.strip("&")
        query = query + "?" + filters
        return query
