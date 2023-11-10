import requests

result = requests.get("http://127.0.0.1:3000/api/alex")
post_result = requests.post("http://127.0.0.1:3000/api:", data={})
print(result.text)
