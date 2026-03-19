import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel
from typing import List

load_dotenv()

HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}


# ── Modelos estruturados ───────────────────────────────────────────────────────

class AgenteDetalhe(BaseModel):
    nome: str                    # Ex: "Agente Extrator"
    funcao: str                  # Descrição clara do papel
    ferramentas: List[str]       # Ex: ["web_search", "pdf_reader"]


class ArquiteturaDetalhe(BaseModel):
    descricao_geral: str         # Como essa arquitetura se aplica ao caso
    agentes: List[AgenteDetalhe] # Lista de agentes com detalhes
    vantagens: List[str]         # Pontos fortes no contexto
    desvantagens: List[str]      # Limitações no contexto


class ArquiteturaDeAgentes(BaseModel):
    arquitetura_1_prompt_chaining: ArquiteturaDetalhe
    arquitetura_2_orchestrator_workers: ArquiteturaDetalhe
    arquitetura_3_parallelization: ArquiteturaDetalhe
    arquitetura_4_routing: ArquiteturaDetalhe
    recomendacao_final: str


# ── Agente Arquiteto ───────────────────────────────────────────────────────────

agente_arquiteto = Agent(
    model=OpenRouterModel("xiaomi/mimo-v2-pro"),
    output_type=ArquiteturaDeAgentes,
    system_prompt=(
        "Você é um arquiteto sênior de sistemas multi-agentes com IA. "
        "Sua especialidade é analisar problemas de negócio e estruturar soluções "
        "usando padrões de orquestração de agentes.\n\n"
        "Você conhece profundamente os 4 padrões de arquitetura abaixo:\n\n"
        "## ARQUITETURA 1 — Prompt Chaining\n"
        "Fluxo sequencial fixo entre agentes. Um agente passa o resultado para o próximo.\n\n"
        "## ARQUITETURA 2 — Orchestrator-Workers\n"
        "Orquestrador decide quais agentes chamar dinamicamente conforme a necessidade.\n\n"
        "## ARQUITETURA 3 — Parallelization\n"
        "Execução simultânea de tarefas independentes por múltiplos agentes.\n\n"
        "## ARQUITETURA 4 — Routing\n"
        "Roteador analisa o input e direciona para o agente especialista correto.\n\n"
        "## SUA TAREFA\n"
        "Para o business case recebido, preencha os campos estruturados de cada arquitetura:\n"
        "- descricao_geral: como essa arquitetura se aplica ao caso\n"
        "- agentes: lista de agentes com nome, função clara e ferramentas específicas\n"
        "  (ferramentas devem ser técnicas e reais, ex: 'web_search', 'sql_query', 'pdf_reader', "
        "  'send_email', 'code_interpreter', 'crm_api', etc.)\n"
        "- vantagens: pontos fortes dessa arquitetura para este caso\n"
        "- desvantagens: limitações ou riscos\n\n"
        "Seja técnico, direto e específico. Responda em português."
    ),
)


# ── Helpers de formatação ──────────────────────────────────────────────────────

CORES = {
    "reset":   "\033[0m",
    "bold":    "\033[1m",
    "titulo":  "\033[1;36m",   # Ciano bold
    "arq":     "\033[1;33m",   # Amarelo bold
    "agente":  "\033[1;32m",   # Verde bold
    "label":   "\033[0;37m",   # Cinza claro
    "rec":     "\033[1;35m",   # Magenta bold
    "plus":    "\033[0;32m",   # Verde
    "minus":   "\033[0;31m",   # Vermelho
}

SEP_DUPLO   = "═" * 70
SEP_SIMPLES = "─" * 70


def c(cor: str, texto: str) -> str:
    """Aplica cor ANSI ao texto."""
    return f"{CORES[cor]}{texto}{CORES['reset']}"


def exibir_arquitetura(titulo: str, arq: ArquiteturaDetalhe) -> None:
    print(c("arq", f"\n{SEP_DUPLO}"))
    print(c("arq", f"  {titulo}"))
    print(c("arq", SEP_DUPLO))

    print(c("label", "\n📋 Descrição Geral:"))
    print(f"   {arq.descricao_geral}\n")

    print(c("label", f"🤖 Agentes ({len(arq.agentes)} no total):"))
    print(c("label", SEP_SIMPLES))

    for i, agente in enumerate(arq.agentes, start=1):
        print(c("agente", f"\n  Agente {i}: {agente.nome}"))
        print(f"  {'Função':<12} {agente.funcao}")
        ferramentas_str = ", ".join(agente.ferramentas) if agente.ferramentas else "nenhuma"
        print(f"  {'Ferramentas':<12} {c('plus', ferramentas_str)}")

    print(c("label", f"\n{SEP_SIMPLES}"))

    if arq.vantagens:
        print(c("label", "✅ Vantagens:"))
        for v in arq.vantagens:
            print(c("plus", f"   + {v}"))

    if arq.desvantagens:
        print(c("label", "\n⚠️  Desvantagens:"))
        for d in arq.desvantagens:
            print(c("minus", f"   - {d}"))


def exibir_analise(resultado: ArquiteturaDeAgentes, business_case: str) -> None:
    print(c("titulo", f"\n{SEP_DUPLO}"))
    print(c("titulo", "  BUSINESS CASE ANALISADO"))
    print(c("titulo", SEP_DUPLO))
    print(f"\n{business_case}\n")

    exibir_arquitetura("ARQUITETURA 1 — PROMPT CHAINING",       resultado.arquitetura_1_prompt_chaining)
    exibir_arquitetura("ARQUITETURA 2 — ORCHESTRATOR-WORKERS",  resultado.arquitetura_2_orchestrator_workers)
    exibir_arquitetura("ARQUITETURA 3 — PARALLELIZATION",       resultado.arquitetura_3_parallelization)
    exibir_arquitetura("ARQUITETURA 4 — ROUTING",               resultado.arquitetura_4_routing)

    print(c("rec", f"\n{SEP_DUPLO}"))
    print(c("rec", "  ⭐  RECOMENDAÇÃO DO ARQUITETO"))
    print(c("rec", SEP_DUPLO))
    print(f"\n{resultado.recomendacao_final}\n")
    print(c("rec", SEP_DUPLO))


# ── Execução interativa ───────────────────────────────────────────────────────

if __name__ == "__main__":
    print(c("titulo", "═" * 70))
    print(c("titulo", "  🧠 ARQUITETO DE SISTEMAS MULTI-AGENTES"))
    print(c("titulo", "═" * 70))

    business_case = input("\nQual é o business case que você quer analisar?\n\n> ")

    if not business_case.strip():
        print("\n❌ Você precisa descrever um business case.")
        exit()

    print("\n⏳ Analisando... aguarde.\n")

    resposta = agente_arquiteto.run_sync(business_case)
    exibir_analise(resposta.output, business_case)

    print(f"\n📊 Chamadas à API: {resposta.usage().requests}")
