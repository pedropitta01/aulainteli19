import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel


load_dotenv()


HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais sobre qualquer assunto.
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




modelo = OpenRouterModel("openai/gpt-4o-mini")




# ── SEM output estruturado — texto livre ─────────────────────────────────────


agente_livre = Agent(
    model=modelo,
    tools=[pesquisar_wikipedia],
    system_prompt="Você pesquisa e analisa temas.",
)


print("=" * 60)
print("SEM OUTPUT ESTRUTURADO — texto livre")
print("=" * 60)


r = agente_livre.run_sync("Analise o tema: machine learning")
print(r.output)
print(f"\nTipo: {type(r.output)}")
# str — como extraio só as aplicações?
# E se amanhã o modelo formatar diferente?




# ── COM output estruturado — objeto Python tipado ────────────────────────────


class AnaliseTema(BaseModel):
    tema: str
    definicao: str
    aplicacoes: list[str]
    conceitos_relacionados: list[str]
    nivel_complexidade: str  # "básico", "intermediário" ou "avançado"


agente_estruturado = Agent(
    model=modelo,
    tools=[pesquisar_wikipedia],
    output_type=AnaliseTema,  # ← força o formato
    system_prompt="Você pesquisa e analisa temas de forma estruturada.",
)


print("\n" + "=" * 60)
print("COM OUTPUT ESTRUTURADO — objeto Python tipado")
print("=" * 60)


r = agente_estruturado.run_sync("Analise o tema: machine learning")
analise = r.output


# Acesso direto — sem parse, sem regex, sem torcer para o formato
print(f"Tema:             {analise.tema}")
print(f"Complexidade:     {analise.nivel_complexidade}")
print(f"Definição:        {analise.definicao[:150]}...")
print(f"\nAplicações:")
for a in analise.aplicacoes:
    print(f"  • {a}")
print(f"\nRelacionado com:  {analise.conceitos_relacionados}")
print(f"\nTipo do objeto:   {type(analise)}")
print(f"Tipo de 'tema':   {type(analise.tema)}")




# ── Por que isso importa para multi-agentes ───────────────────────────────────


print("\n" + "=" * 60)
print("POR QUE IMPORTA — passando entre agentes")
print("=" * 60)


# Com texto livre você faria isso — frágil:
# proximo_agente.run_sync(f"Com base nisso: {r_livre.output}...")
# O próximo agente recebe um parágrafo e precisa adivinhar onde está cada info


# Com output estruturado você faz isso — robusto:
print(f"Passando para o próximo agente:")
print(f"  tema:        {analise.tema}")
print(f"  aplicacoes:  {analise.aplicacoes}")
print(f"  complexidade: {analise.nivel_complexidade}")
# Acesso direto a cada campo — sem ambiguidade
