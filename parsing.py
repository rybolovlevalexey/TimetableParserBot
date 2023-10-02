import requests
import bs4
from datetime import date, timedelta
import models
import csv
from pprint import pprint


def week_timetable_dict(url: str, next_week: bool = False) -> dict[str, list]:
    if next_week:
        today = date.today()
        days_to_monday = (7 - today.weekday()) % 7
        next_monday = today + timedelta(days=days_to_monday)
        url += f"/{next_monday}"
    responce = requests.get(url)
    html = bs4.BeautifulSoup(responce.content, "html.parser")
    timetable = dict()  # {day: [subjects with info]}

    for elem in html.find_all(name="div", attrs={"class": "panel panel-default"}):
        block = bs4.BeautifulSoup(str(elem), "html.parser")
        day = block.find(name="h4").text.strip()
        timetable[day] = list()
        for elem in block.select(".panel-collapse > .common-list-item"):
            info = list(filter(lambda x: len(x) > 0,
                               map(lambda x: x.strip(), elem.text.strip().split("\n"))))
            timetable[day].append(info)
    return timetable


def removing_unnecessary_items(timetable: dict[str, list]) -> dict[str, list]:
    result = dict()
    for key, value in timetable.items():
        result[key] = list()
        for i in range(len(value)):
            if i == 0 and len(value) == 1:
                result[key] += [value[i]]
            elif i + 1 < len(value):
                if value[i][0] != value[i + 1][0] or \
                        (value[i][0] == value[i + 1][0] and
                         (len(result[key]) == 0 or result[key][-1][0] != value[i][0])):
                    result[key] += [value[i]]
            else:
                if i != 0 and value[i - 1][0] != value[i][0]:
                    result[key] += [value[i]]
    return result


# добавить сохранение в файл вместе с ссылками
def make_links_to_educational_directions():  # пока что только Мат-Мех бакалавриат
    # очистка таблицы со ссылками на образовательные направления
    models.EducationalDirection().delete().execute()
    # образовательные возможности мат-меха
    url = list(elem.get("url") for elem in csv.DictReader(open("links for parsing.csv", "r"))
               if elem.get("name") == "Faculty of Mathematics and Mechanics")[0].strip()
    resp = requests.get(url)
    result = bs4.BeautifulSoup(resp.content, "html.parser")
    parse = bs4.BeautifulSoup(
        str(result.find_all(name="div", attrs={"class": "panel panel-default"})),
        "html.parser")  # блоки образовательных возможностей мат-меха

    for panel_default in parse:
        # название образовательного блока
        title = bs4.BeautifulSoup(str(panel_default), "html.parser").find("a", attrs={
            "data-toggle": "collapse"})
        if title is not None:
            if title.text.strip() == "Bachelor Studies":
                # проход по всем списочным элементам внутри данного блока
                for elem in bs4.BeautifulSoup(
                        str(panel_default), "html.parser"). \
                        find_all(name="li", attrs={"class": "common-list-item row"}):
                    educational_program, years = list(), list()
                    sp = list(filter(lambda x: len(x) > 0,
                                     map(lambda x: x.strip(),
                                         elem.text.strip().split(" "))))
                    for elem1 in sp:
                        if elem1.isdigit():
                            years.append(elem1)
                        else:
                            educational_program.append(elem1)
                    educational_program = " ".join(educational_program)
                    educational_links = dict()
                    with models.database:
                        for link in bs4.BeautifulSoup(str(elem), "html.parser"). \
                                find_all("a", attrs={"data-toggle": "tooltip"}):
                            models.EducationalDirection(name=educational_program,
                                                        year=link.text.strip(),
                                                        url="https://timetable.spbu.ru" +
                                                            link.get("href")).save()

    return "Ok"


if __name__ == "__main__":
    link = list(elem.get("url") for elem in csv.DictReader(open("links for parsing.csv", "r"))
                if elem.get("name") == "Group tp22b07")[0].strip()
    pprint(removing_unnecessary_items(week_timetable_dict(link, True)))
    print(make_links_to_educational_directions())
