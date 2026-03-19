import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


# ── Mesma função, duas docstrings diferentes ──────────────────────────────────

def pesquisar_v1(termo: str) -> str:
    """Pesquisa."""   # ← o modelo não sabe quando usar isso
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
        return resumo.json().get("extract", "Sem resumo.") if resumo.status_code == 200 else "Não encontrado."
    except Exception as e:
        return f"Erro: {e}"


def pesquisar_v2(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais sobre qualquer assunto.
    Sempre use esta ferramenta antes de responder — nunca responda de memória.
    """
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
        return resumo.json().get("extract", "Sem resumo.") if resumo.status_code == 200 else "Não encontrado."
    except Exception as e:
        return f"Erro: {e}"


modelo = OpenRouterModel("openai/gpt-4o-mini")
pergunta = "O que é uma rede neural artificial?"

agente_v1 = Agent(
    model=modelo,
    tools=[pesquisar_v1],
    system_prompt="Responda perguntas sobre tecnologia.",
)

agente_v2 = Agent(
    model=modelo,
    tools=[pesquisar_v2],
    system_prompt="Responda perguntas sobre tecnologia.",
)

print("=" * 60)
print("DOCSTRING VAGA:")
print("=" * 60)
r1 = agente_v1.run_sync(pergunta)
print(r1.output[:300])
print(f"Chamadas: {r1.usage().requests}")
# Provavelmente 1 — o modelo não usou a ferramenta

print("\n" + "=" * 60)
print("DOCSTRING PRECISA:")
print("=" * 60)
r2 = agente_v2.run_sync(pergunta)
print(r2.output[:300])
print(f"Chamadas: {r2.usage().requests}")
# Provavelmente 2+ — o modelo usou a ferramenta

print("""
Observe o número de chamadas:
  Docstring vaga   → provavelmente 1 chamada → respondeu de memória
  Docstring boa    → provavelmente 2+ chamadas → buscou antes de responder

A docstring é o contrato da ferramenta.
Vaga = ferramenta ignorada. Precisa = ferramenta usada corretamente.
""")
