import requests
from fake_useragent import UserAgent
import bs4
from pprint import pprint
from datetime import date, timedelta
import csv
from dataclasses import dataclass


class ParsingTimeTable:
    def __init__(self):
        self.base_url = "https://timetable.spbu.ru"
        self.cookie = {"_culture": "ru"}
        self.program_levels = ["Бакалавриат", "Магистратура"]
        self.user_agent = UserAgent().random

    def parsing_faculties_links(self) -> dict[str, str] | None:
        """
        Парсинг ссылок на факультеты
        :return: Словарь: ключ - название факультета, значение - ссылка на данный факультет
        """
        resp = requests.get(self.base_url, headers={"User-Agent": self.user_agent}, cookies=self.cookie)
        if resp.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        result: dict[str, str] = dict()

        for line in soup.find_all("div", class_="col-sm-6")[0].find("ul", class_="list-group").find_all("li"):
            name, link = line.text.strip(), line.find("a").get("href").strip()
            if not link.startswith("http"):
                link = self.base_url + link if link.startswith("/") else self.base_url + "/" + link
            result[name] = link

        return result

    def parsing_edu_programs_links(self, faculties_link) -> dict[(str, str), str] | None:
        """
        Парсинг ссылок на образовательные направления
        :param faculties_link: на вход подаётся ссылка на факультет
        :return: Словарь: ключ - (название направления, год поступления), значение - ссылка на данное направление
        """
        resp = requests.get(faculties_link, headers={"User-Agent": self.user_agent}, cookies=self.cookie)
        if resp.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        result: dict[(str, str), str] = dict()

        # проход по всем образовательным уровня
        for level_block in soup.find("div", class_="panel-group").find_all(class_="panel panel-default"):
            if not level_block.find(class_="panel-heading").text.strip() in self.program_levels:
                continue
            # проход по всем программам в рамках данного образовательного уровня
            for program in level_block.find("ul").find_all("li", recursive=False):
                if len(program.find_all("a")) == 0:
                    continue
                program_name = program.find(class_="col-sm-5").text.strip()
                # проход в цикле по всем годам поступления данной образовательной программы
                for year_elem in program.find_all(class_="col-sm-1"):
                    year, program_year_url = year_elem.text.strip(), self.base_url + year_elem.find("a").get("href")
                    result[(program_name, year)] = program_year_url

        return result

    def parsing_groups_studying_links(self, program_link) -> None | dict[str, str]:
        """
        Парсинг ссылок на группы в рамках данного направления по текущему году (промежуточная аттестация будет отдельно)
        :param program_link: Ссылка на данное направление
        :return: Словарь: ключ - название группы, значение - ссылка на группу
        """
        resp = requests.get(program_link, headers={"User-Agent": self.user_agent}, cookies=self.cookie)
        if resp.status_code != 200:
            return None
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        result: dict[str, str] = dict()

        # проход внутри блока с расписанием образования, а не промежуточной аттестации
        for group_line in soup.find_all(class_="panel panel-default")[1].find("ul").find_all("li"):
            group_name = group_line.find("div").find("div").text.strip()
            group_link = self.base_url + str(group_line.find("div").get("onclick").split("=")[1].strip())[1:-1]
            result[group_name] = group_link

        return result


ex = ParsingTimeTable()
# pprint(ex.parsing_faculties_links())
# pprint(ex.parsing_edu_programs_links("https://timetable.spbu.ru/MATH"))
pprint(ex.parsing_groups_studying_links("https://timetable.spbu.ru/MATH/StudyProgram/15128"))