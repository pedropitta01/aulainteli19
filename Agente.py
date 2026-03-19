import requests
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel

load_dotenv()

HEADERS = {"User-Agent": "AulaAgentes/1.0 (aula didatica)"}

# ── Output estruturado do Agente Arquiteto ─────────────────────────────────────
class ArquiteturaDeAgentes(BaseModel):
    arquitetura_1_prompt_chaining: str
    arquitetura_2_orchestrator_workers: str
    arquitetura_3_parallelization: str
    arquitetura_4_routing: str
    recomendacao_final: str


# ── Agente Arquiteto ───────────────────────────────────────────────────────────
agente_arquiteto = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    output_type=ArquiteturaDeAgentes,
    system_prompt=(
        "Você é um arquiteto sênior de sistemas multi-agentes com IA. "
        "Sua especialidade é analisar problemas de negócio e estruturar soluções "
        "usando padrões de orquestração de agentes.\n\n"

        "Você conhece profundamente os 4 padrões de arquitetura abaixo:\n\n"

        "## ARQUITETURA 1 — Prompt Chaining\n"
        "Agentes especializados executam em sequência fixa definida no código. "
        "A saída de um vira a entrada do próximo (via output_type estruturado). "
        "O fluxo é sempre o mesmo, independente da pergunta. "
        "Os agentes não sabem que fazem parte de um pipeline.\n"
        "Ideal para: fluxos previsíveis, tarefas sequenciais com dependência clara entre etapas, "
        "pipelines de transformação de dados, geração de documentos em etapas.\n\n"

        "## ARQUITETURA 2 — Orchestrator-Workers\n"
        "Um agente orquestrador decide em runtime quais workers acionar e em qual ordem, "
        "com base na pergunta recebida. Os workers são ferramentas do orquestrador. "
        "O orquestrador não tem especialidade, apenas sabe delegar. "
        "O fluxo é dinâmico — cada pergunta pode acionar uma combinação diferente de workers.\n"
        "Ideal para: problemas com múltiplos caminhos possíveis, perguntas abertas, "
        "assistentes inteligentes que precisam combinar habilidades diferentes.\n\n"

        "## ARQUITETURA 3 — Parallelization\n"
        "Tarefas independentes entre si são executadas simultaneamente com async/await e asyncio.gather. "
        "O resultado de A não depende de B, então não há motivo para esperar. "
        "Reduz drasticamente o tempo de execução quando há múltiplas subtarefas paralelas.\n"
        "Ideal para: análises de múltiplas fontes ao mesmo tempo, geração simultânea de variações, "
        "consultas independentes que precisam ser consolidadas ao final.\n\n"

        "## ARQUITETURA 4 — Routing\n"
        "Um agente roteador classifica a pergunta e transfere para o especialista correto, "
        "que responde diretamente. O roteador não sintetiza nada — apenas direciona. "
        "Cada especialista é autônomo e completo para seu domínio.\n"
        "Ideal para: sistemas com domínios bem definidos e separados, chatbots com múltiplas "
        "áreas de atuação, suporte técnico com categorias distintas.\n\n"

        "## SUA TAREFA\n"
        "Quando receber um business case, você deve:\n"
        "1. Para cada uma das 4 arquiteturas, descrever como ela seria aplicada especificamente "
        "ao problema apresentado — com exemplos concretos dos agentes envolvidos, "
        "o fluxo de dados, os papéis de cada agente e as vantagens naquele contexto.\n"
        "2. Ao final, dar sua recomendação fundamentada de qual arquitetura (ou combinação) "
        "seria a mais indicada para o caso, justificando com base em: complexidade do fluxo, "
        "variabilidade das entradas, necessidade de paralelismo e clareza dos domínios.\n\n"
        "Seja técnico, específico e direto. Evite respostas genéricas — "
        "cada resposta deve ser moldada ao business case recebido.\n"
        "Responda sempre em português."
    ),
)


# ── Função utilitária para exibir o resultado formatado ───────────────────────
def exibir_analise(resultado: ArquiteturaDeAgentes, business_case: str) -> None:
    separador = "=" * 70

    print(separador)
    print("BUSINESS CASE ANALISADO:")
    print(separador)
    print(business_case)

    print(f"\n{separador}")
    print("ARQUITETURA 1 — PROMPT CHAINING")
    print(separador)
    print(resultado.arquitetura_1_prompt_chaining)

    print(f"\n{separador}")
    print("ARQUITETURA 2 — ORCHESTRATOR-WORKERS")
    print(separador)
    print(resultado.arquitetura_2_orchestrator_workers)

    print(f"\n{separador}")
    print("ARQUITETURA 3 — PARALLELIZATION")
    print(separador)
    print(resultado.arquitetura_3_parallelization)

    print(f"\n{separador}")
    print("ARQUITETURA 4 — ROUTING")
    print(separador)
    print(resultado.arquitetura_4_routing)

    print(f"\n{separador}")
    print("⭐  RECOMENDAÇÃO DO ARQUITETO")
    print(separador)
    print(resultado.recomendacao_final)
    print(separador)


# ── Business case de exemplo ───────────────────────────────────────────────────
business_case = (
    "Uma empresa de e-commerce quer automatizar o atendimento ao cliente. "
    "Os clientes entram em contato com dúvidas sobre: rastreamento de pedidos, "
    "trocas e devoluções, problemas técnicos no site e dúvidas sobre produtos. "
    "O volume é alto (milhares de atendimentos/dia) e a empresa quer respostas "
    "rápidas, precisas e personalizadas. Alguns casos exigem consultar múltiplos "
    "sistemas ao mesmo tempo (estoque, logística, histórico do cliente)."
)

# ── Execução ───────────────────────────────────────────────────────────────────
print("Analisando business case... aguarde.\n")
resposta = agente_arquiteto.run_sync(business_case)
exibir_analise(resposta.output, business_case)
print(f"\nChamadas à API: {resposta.usage().requests}")