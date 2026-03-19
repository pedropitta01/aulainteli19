import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel


load_dotenv()


HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


# Contador para mostrar quantas vezes a ferramenta foi chamada
contador = {"n": 0}


def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais sobre qualquer assunto.
    Para comparações, pesquise cada tema separadamente.
    """
    contador["n"] += 1
    print(f"  [Tool call #{contador['n']}] pesquisando '{termo}'...")


    try:
        busca = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search",
                    "srsearch": termo, "format": "json", "srlimit": 1},
            timeout=5, headers=HEADERS,
        )
        resultados = busca.json().get("query", {}).get("search", [])
        if not resultados:
            return f"Não encontrei nada sobre '{termo}'."
        titulo = resultados[0]["title"]
        resumo = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/page/summary/{titulo.replace(' ', '_')}",
            timeout=5, headers=HEADERS,
        )
        texto = resumo.json().get("extract", "Sem resumo.") if resumo.status_code == 200 else "Não encontrado."
        print(f"  [#{contador['n']} concluído — artigo: {titulo}]")
        return f"[Artigo: {titulo}]\n{texto}"
    except Exception as e:
        return f"Erro: {e}"




agente = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    tools=[pesquisar_wikipedia],
    system_prompt=(
        "Você é um assistente de pesquisa. "
        "Para comparações, pesquise CADA tema separadamente antes de responder."
    ),
)


print("=" * 60)
print("Loop ReAct — múltiplos tool calls")
print("=" * 60)
print("Pergunta enviada — observe os tool calls acontecendo:\n")


result = agente.run_sync(
    "Compare machine learning e deep learning: "
    "o que são, qual a diferença e como se relacionam?"
)


print("\nRESPOSTA FINAL:")
print(result.output)
print(f"\nTool calls executados:    {contador['n']}")
print(f"Chamadas ao servidor:     {result.usage().requests}")
print("""
O modelo decidiu sozinho:
  → pesquisar machine learning
  → pesquisar deep learning
  → comparar os dois e responder


Você não programou essa sequência.
O modelo leu a pergunta, raciocinou e decidiu o que fazer.
Isso é o loop ReAct em ação.
""")
