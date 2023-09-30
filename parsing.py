import requests
import datetime
import bs4
from pprint import pprint


links_file = open("links for parsing.txt")
url = links_file.readline().strip()
responce = requests.get(url)
html = bs4.BeautifulSoup(responce.content, "html.parser")
timetable = dict()  # {day: [subjects with info]}

for elem in html.find_all(name="div", attrs={"class": "panel panel-default"}):
    block = bs4.BeautifulSoup(str(elem), "html.parser")
    day = block.find(name="h4").text.strip()
    timetable[day] = list()
    for elem in block.select(".panel-collapse > .common-list-item"):
        info = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), elem.text.strip().split("\n"))))
        timetable[day].append(info)
