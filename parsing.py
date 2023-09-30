import requests
import datetime
import bs4


links_file = open("links for parsing.txt")
url = links_file.readline().strip()
responce = requests.get(url)
html = bs4.BeautifulSoup(responce.content, "html.parser")

for elem in html.select(".panel-collapse > .common-list-item"):
    info = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), elem.text.strip().split("\n"))))
    time, subject, place, teacher = info
    print(time)
    break