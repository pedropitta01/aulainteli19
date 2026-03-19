import os

import requests
from dotenv import load_dotenv

print("Verificacao de modelos disponiveis no OpenRouter")

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    print("Erro: a variavel API_KEY nao foi encontrada no arquivo .env.")
else:
    url = "https://openrouter.ai/api/v1/models"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://local.course.example",
        "X-Title": "Verificador de modelos disponiveis",
    }

    resposta = requests.get(url, headers=headers, timeout=30)

    if resposta.status_code != 200:
        print("Erro na requisicao:", resposta.status_code)
        print(resposta.text)
    else:
        dados = resposta.json()
        modelos = dados.get("data", [])

        print("Total de modelos encontrados:", len(modelos))
        print()

        for modelo in modelos:
            print(modelo["id"])
