from models import EducationalDirection

# возможные callback от сообщения с настройками
SETTINGS_CALLBACKS = ["Close settings", "Choosing subgroup", "Delete account"]
INSTITUTE_FACULTIES = ["Мат-мех"]  # список с факультетами, необходимо расширить в будущем
EDUCATION_DEGREES = ["Бакалавриат", "Магистратура"]  # список степеней образования
EDUCATION_PROGRAMS = sorted(set(elem.name for elem in EducationalDirection.select()))
EDUCATION_PROGRAMS_SHORT = list(map(lambda x: x[:60], EDUCATION_PROGRAMS))
YEARS = list(i for i in range(2020, 2024))