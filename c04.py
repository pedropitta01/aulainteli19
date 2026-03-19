import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais sobre qualquer assunto.
    Pode ser chamada múltiplas vezes para temas diferentes.
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
        texto = resumo.json().get("extract", "Sem resumo.") if resumo.status_code == 200 else "Não encontrado."
        return f"[Artigo: {titulo}]\n{texto}"


    except Exception as e:
        return f"Erro: {e}"




modelo = OpenRouterModel("xiaomi/mimo-v2-pro")
pergunta = "O que é processamento de linguagem natural?"


# ── Sem ferramenta — responde de memória ──────────────────────────────────────
agente_sem = Agent(
    model=modelo,
    system_prompt="Você é um assistente de pesquisa.",
)


# ── Com ferramenta — busca antes de responder ─────────────────────────────────
agente_com = Agent(
    model=modelo,
    tools=[pesquisar_wikipedia],
    system_prompt=(
        "Você é um assistente de pesquisa. "
        "Sempre pesquise o tema antes de responder — nunca responda de memória."
    ),
)


print("=" * 60)
print("SEM FERRAMENTA:")
print("=" * 60)
r1 = agente_sem.run_sync(pergunta)
print(r1.output)
print(f"\nChamadas à API: {r1.usage().requests}")


print("\n" + "=" * 60)
print("COM FERRAMENTA:")
print("=" * 60)
r2 = agente_com.run_sync(pergunta)
print(r2.output)
print(f"\nChamadas à API: {r2.usage().requests}")
