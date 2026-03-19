from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
import requests

load_dotenv()

def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais e atualizadas sobre qualquer assunto.
    Prefira termos específicos: 'Redes neurais artificiais' em vez de 'IA'.
    """
    url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo.replace(' ', '_')}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return f"Não encontrei informações sobre '{termo}'."
        return r.json().get("extract", "Sem resumo disponível.")
    except Exception as e:
        return f"Erro: {e}"


# Sem ferramenta — responde de memória, pode alucinar
agente_sem_ferramenta = Agent(
    model=OpenRouterModel("xiaomi/mimo-v2-pro"),
    system_prompt="Você é um assistente de pesquisa.",
)

# Com ferramenta — busca informação real antes de responder
agente_com_ferramenta = Agent(
    model=OpenRouterModel("xiaomi/mimo-v2-pro"),
    tools=[pesquisar_wikipedia],
    system_prompt=(
        "Você é um assistente de pesquisa. "
        "Sempre pesquise o tema antes de responder — nunca responda de memória."
    ),
)

pergunta = "O que é processamento de linguagem natural?"

r1 = agente_sem_ferramenta.run_sync(pergunta)
r2 = agente_com_ferramenta.run_sync(pergunta)

print("SEM FERRAMENTA:")
print(r1.output[:300])
print(f"Chamadas: {r1.usage().requests}")

print("\nCOM FERRAMENTA:")
print(r2.output[:300])
print(f"Chamadas: {r2.usage().requests}")
# O segundo vai ter mais chamadas — foi buscar antes de responder