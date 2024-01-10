from dataclasses import dataclass, field


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

