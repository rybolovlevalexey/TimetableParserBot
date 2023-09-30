import requests
import bs4
from pprint import pprint
from datetime import date, timedelta


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


def make_links_to_educational_directions():  # пока что только Мат-Мех бакалавриат
    url = open("links for parsing.txt", "r").readlines()[1]  # образовательные возможности мат-меха
    responce = requests.get(url)
    result = bs4.BeautifulSoup(responce.content, "html.parser")
    parse = bs4.BeautifulSoup(
        str(result.find_all(name="div", attrs={"class": "panel panel-default"})),
        "html.parser")  # блоки образовательных возможностей мат-меха

    for panel_default in parse:
        # название образовательного блока
        title = bs4.BeautifulSoup(str(panel_default), "html.parser").find("a", attrs={"data-toggle": "collapse"})
        if title is not None:
            if title.text.strip() == "Bachelor Studies":
                print(title.text.strip())
                # проход по всем списочным элементам внутри данного блока
                for elem in bs4.BeautifulSoup(
                        str(panel_default), "html.parser").\
                        find_all(name="li", attrs={"class": "common-list-item row"}):
                    print(*filter(lambda x: len(x) > 0,
                                  map(lambda x: x.strip(),
                                      elem.text.strip().split(" "))))


if __name__ == "__main__":
    # links_file = open("links for parsing.txt")
    # link = links_file.readline().strip()
    # pprint(removing_unnecessary_items(week_timetable_dict(link, True)))
    make_links_to_educational_directions()