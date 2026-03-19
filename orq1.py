import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel


load_dotenv()


HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}
modelo  = OpenRouterModel("openai/gpt-4o-mini")




# ── Ferramenta ────────────────────────────────────────────────────────────────


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




# ── Agente 1: Pesquisador ─────────────────────────────────────────────────────
# Responsabilidade única: buscar informações brutas
# NÃO analisa, NÃO opina — só pesquisa e organiza


class InfoPesquisada(BaseModel):
    temas_pesquisados: list[str]
    informacoes: dict[str, str]  # tema → texto encontrado
    lacunas: list[str]           # temas sem informação suficiente


agente_pesquisador = Agent(
    model=modelo,
    tools=[pesquisar_wikipedia],
    output_type=InfoPesquisada,
    system_prompt=(
        "Você pesquisa temas na Wikipedia e organiza as informações. "
        "Para cada tema da lista, busque e registre o que encontrou. "
        "NÃO analise, NÃO opine — apenas pesquise e organize."
    ),
)




# ── Agente 2: Analista ────────────────────────────────────────────────────────
# Responsabilidade única: encontrar conexões
# NÃO pesquisa, NÃO escreve relatório — só analisa


class Analise(BaseModel):
    conexoes: list[str]   # relações entre os temas
    tema_central: str     # o fio condutor entre todos
    insights: list[str]   # descobertas relevantes
    complexidade: str     # "básico", "intermediário" ou "avançado"


agente_analista = Agent(
    model=modelo,
    output_type=Analise,
    system_prompt=(
        "Você analisa informações pesquisadas e encontra conexões entre temas. "
        "NÃO pesquise mais — trabalhe só com o que foi fornecido. "
        "NÃO escreva relatório — apenas analise."
    ),
)




# ── Agente 3: Redator ─────────────────────────────────────────────────────────
# Responsabilidade única: transformar análise em texto legível
# NÃO pesquisa, NÃO analisa — só redige


class Relatorio(BaseModel):
    titulo: str
    resumo_executivo: str   # máx 3 frases, sem jargão, para gestores
    corpo: str              # explicação completa para leigos
    conclusao: str
    proximos_passos: list[str]


agente_redator = Agent(
    model=modelo,
    output_type=Relatorio,
    system_prompt=(
        "Você transforma análises técnicas em relatórios claros. "
        "Resumo executivo: máximo 3 frases, zero jargão, foco em impacto. "
        "NÃO pesquise, NÃO analise — apenas redija com o que foi fornecido."
    ),
)




# ── O pipeline ────────────────────────────────────────────────────────────────
# O fluxo está aqui — não nos agentes
# Cada agente recebe só o que precisa — não o contexto inteiro


def pipeline(temas: list[str]) -> Relatorio:


    # Passo 1: pesquisa
    print("🔍 [1/3] Pesquisando temas...")
    info = agente_pesquisador.run_sync(
        f"Pesquise os temas: {', '.join(temas)}"
    ).output
    print(f"   Pesquisados: {info.temas_pesquisados}")
    if info.lacunas:
        print(f"   Lacunas:     {info.lacunas}")


    # Valida antes de continuar — erro aqui é melhor que erro no passo 3
    if not info.informacoes:
        raise ValueError("Pesquisador não encontrou nada — verifique os temas.")


    # Passo 2: análise
    # Recebe o output estruturado do passo 1 — não texto livre
    print("\n🧠 [2/3] Analisando conexões...")
    analise = agente_analista.run_sync(
        "Analise as informações encontradas:\n\n" +
        "\n\n".join([
            f"TEMA: {t}\nINFO: {i}"
            for t, i in info.informacoes.items()
        ])
    ).output
    print(f"   Tema central: {analise.tema_central}")
    print(f"   Complexidade: {analise.complexidade}")
    print(f"   Insights:     {len(analise.insights)} encontrados")


    # Passo 3: redação
    # Recebe só o necessário — não o HTML bruto da Wikipedia
    print("\n✍️  [3/3] Redigindo relatório...")
    relatorio = agente_redator.run_sync(
        f"Redija um relatório com base na análise:\n\n"
        f"Temas: {info.temas_pesquisados}\n"
        f"Tema central: {analise.tema_central}\n"
        f"Conexões: {analise.conexoes}\n"
        f"Insights: {analise.insights}\n"
        f"Complexidade: {analise.complexidade}"
    ).output


    return relatorio




# ── Rodando ───────────────────────────────────────────────────────────────────


resultado = pipeline([
    "machine learning",
    "redes neurais artificiais",
    "deep learning",
])


print("\n" + "=" * 60)
print(f"TÍTULO:\n{resultado.titulo}")
print(f"\nRESUMO EXECUTIVO:\n{resultado.resumo_executivo}")
print(f"\nCORPO:\n{resultado.corpo}")
print(f"\nCONCLUSÃO:\n{resultado.conclusao}")
print(f"\nPRÓXIMOS PASSOS:")
for p in resultado.proximos_passos:
    print(f"  • {p}")