import requests
import uuid
import json
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

client_secret = "e80abacb-80ed-419e-bb4a-23ede64492d7"
client_id = "4c1a3286-c1ee-42e9-8429-956ad84648a0"
auth_data = "NGMxYTMyODYtYzFlZS00MmU5LTg0MjktOTU2YWQ4NDY0OGEwOmU4MGFiYW" \
            "NiLTgwZWQtNDE5ZS1iYjRhLTIzZWRlNjQ0OTJkNw=="
chat = GigaChat(credentials=auth_data, verify_ssl_certs=False)
text = """Сформулируй в более удобном виде, что нужно сделать исходя из этого сообщения:
        Добрый день. Можно установить цену списания фонаря 605000724AA в данной 
        реализации, по минимсальной цене из вот поступления № ОМ000000312 от
        10.09.2023 . Пришло 2 одинаковых фонаря но по разной цене и 
        программа усреднила стоимость..., и теперь данная продажа в 
        минус получается..."""
messages = [HumanMessage(content=text)]
result = chat(messages)
print(result.content)


def getting_token():
    url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
    headers = {
        'Authorization': f'Bearer {auth_data}',
        'RqUID': str(uuid.uuid4()),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    response = requests.post(url, headers=headers, data=data, verify=False)
    return response


def giga_work():
    token = json.loads(getting_token().content.strip())["access_token"]
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "model": "GigaChat:latest",
        "messages": [
            {
                "role": "user",
                "content": text
            }
        ]
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response.content
