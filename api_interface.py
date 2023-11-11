import requests

# добавление нового пользователя
# post_data = {"name": "alex", "group": "22.Б07-мм"}
# post_result = requests.post("http://127.0.0.1:3000/api", data=json.dumps(post_data),
#                             headers={'Content-Type': 'application/json'})

# получение расписания по логину пользователя
result = requests.get("http://127.0.0.1:3000/api/alex")
print(result.text)