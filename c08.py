import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel


load_dotenv()


HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


chamadas_ferramenta = {"n": 0}


def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use apenas quando a informação ainda não estiver disponível na conversa.
    """
    chamadas_ferramenta["n"] += 1
    print(f"  >>> FERRAMENTA CHAMADA #{chamadas_ferramenta['n']}: '{termo}'")
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




agente = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    tools=[pesquisar_wikipedia],
    system_prompt=(
        "Você é um assistente de pesquisa. "
        "Pesquise quando precisar de informações novas. "
        "Se a informação já está no histórico da conversa, use-a diretamente — não pesquise de novo."
    ),
)




# ── SEM memória ───────────────────────────────────────────────────────────────


print("=" * 60)
print("SEM MEMÓRIA")
print("=" * 60)


chamadas_ferramenta["n"] = 0
print("\n--- Mensagem 1 ---")
r1 = agente.run_sync("Pesquise machine learning e me explique com suas palavras.")
print(r1.output)
print(f"Chamadas ao servidor: {r1.usage().requests} | Ferramenta: {chamadas_ferramenta['n']}x")


chamadas_ferramenta["n"] = 0
print("\n--- Mensagem 2 ---")
r2 = agente.run_sync("Faça um resumo em 3 linhas do que você explicou.")
print(r2.output)
print(f"Chamadas ao servidor: {r2.usage().requests} | Ferramenta: {chamadas_ferramenta['n']}x")
# Não sabe o que foi explicado — vai pesquisar de novo ou dizer que não sabe




# ── COM memória ───────────────────────────────────────────────────────────────


print("\n" + "=" * 60)
print("COM MEMÓRIA")
print("=" * 60)


historico = []
chamadas_ferramenta["n"] = 0


print("\n--- Mensagem 1 ---")
r1 = agente.run_sync(
    "Pesquise machine learning e me explique com suas palavras.",
    message_history=historico
)
historico = r1.all_messages()
print(r1.output)
print(f"Chamadas ao servidor: {r1.usage().requests} | Ferramenta: {chamadas_ferramenta['n']}x")


chamadas_ferramenta["n"] = 0
print("\n--- Mensagem 2 ---")
r2 = agente.run_sync(
    "Faça um resumo em 3 linhas do que você explicou.",
    message_history=historico
)
historico = r2.all_messages()
print(r2.output)
print(f"Chamadas ao servidor: {r2.usage().requests} | Ferramenta: {chamadas_ferramenta['n']}x")
# Ferramenta = 0 — resumiu o que já estava no histórico, não precisou buscar


chamadas_ferramenta["n"] = 0
print("\n--- Mensagem 3 ---")
r3 = agente.run_sync(
    "Explique isso como se eu tivesse 10 anos.",
    message_history=historico
)
historico = r3.all_messages()
print(r3.output)
print(f"Chamadas ao servidor: {r3.usage().requests} | Ferramenta: {chamadas_ferramenta['n']}x")
# Ferramenta = 0 — reescreveu o que já sabia, sem buscar nada novo