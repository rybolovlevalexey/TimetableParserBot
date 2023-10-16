import requests
import bs4
from datetime import date, timedelta
import models
import csv
from dataclasses import dataclass
from pprint import pprint


@dataclass
class EducationalDirectionLine:
    name: str
    year: int
    url: str

    def __str__(self):
        return f"{self.name} {self.year} {self.url}"


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
        for elem1 in block.select(".panel-collapse > .common-list-item"):
            info = list(filter(lambda x: len(x) > 0,
                               map(lambda x: x.strip(), elem1.text.strip().split("\n"))))
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


def load_links_to_educational_directions():
    # очистка таблицы со ссылками на образовательные направления
    # models.EducationalDirection().delete().execute()

    with models.db:
        for elem in make_links_to_educational_directions():
            models.EducationalDirection(name=elem.name,
                                        year=elem.year,
                                        url=elem.url).save()


# создание списка со ссылками на образовательные направления, пока что только Мат-Мех бакалавриат
def make_links_to_educational_directions() -> list[EducationalDirectionLine]:
    func_result = list()
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
                    for link in bs4.BeautifulSoup(str(elem), "html.parser"). \
                            find_all("a", attrs={"data-toggle": "tooltip"}):
                        func_result.append(EducationalDirectionLine(name=educational_program,
                                                                    year=link.text.strip(),
                                                                    url="https://timetable.spbu.ru" +
                                                                        link.get("href")))
    return func_result


# наполнение базы данных ссылками на конкретные группы
def make_links_to_groups() -> bool:
    # if make_links_to_educational_directions():
    #     print(f"Таблица 'programs directions' наполнена ссылками корректно")
    for line in models.EducationalDirection.select():  # ссылки на конкретное направление
        # страница с группами
        parser = bs4.BeautifulSoup(requests.get(line.url).content, "html.parser")
        # блоки
        for block in parser.find_all(name="div",
                                     attrs={"class": "panel panel-default"}):
            # текущий учебный семестр, аттестация, аттестация(долги), ...
            title = bs4.BeautifulSoup(str(block), "html.parser") \
                .find("a", attrs={"data-toggle": "collapse"}).text.strip()
            if title == "Current academic year 2023-2024":
                groups_info = bs4.BeautifulSoup(str(block), "html.parser") \
                    .find_all("div", attrs={"class": "tile"})
                for group in groups_info:
                    group_name = group.text.strip().split()[0]
                    group_url = group.get("onclick")
                    start, finish = group_url.find("'"), len(group_url) - "".join(
                        reversed(group_url)).find("'")
                    models.GroupDirection(educational_program_id=line.id,
                                          group_name=group_name,
                                          url=f"https://timetable.spbu.ru"
                                              f"{group_url[start + 1: finish - 1]}").save()
    return True


if __name__ == "__main__":
    pass