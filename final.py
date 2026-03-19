import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel
from typing import List
import subprocess
import sys
import tempfile
import os

load_dotenv()

# ── Modelos estruturados ───────────────────────────────────────────────────────

class AgenteDetalhe(BaseModel):
    nome: str
    funcao: str
    ferramentas: List[str]

class ArquiteturaDetalhe(BaseModel):
    descricao_geral: str
    agentes: List[AgenteDetalhe]
    vantagens: List[str]
    desvantagens: List[str]

class ArquiteturaDeAgentes(BaseModel):
    arquitetura_1_prompt_chaining: ArquiteturaDetalhe
    arquitetura_2_orchestrator_workers: ArquiteturaDetalhe
    arquitetura_3_parallelization: ArquiteturaDetalhe
    arquitetura_4_routing: ArquiteturaDetalhe
    recomendacao_final: str

class CodigoGerado(BaseModel):
    codigo_python: str
    descricao_implementacao: str

# ── Agentes ────────────────────────────────────────────────────────────────────

agente_arquiteto = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
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

agente_gerador = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    output_type=CodigoGerado,
    system_prompt=(
        "Você é um engenheiro sênior especialista em pydantic-ai e OpenRouter.\n\n"
        "Sua tarefa é gerar código Python funcional que implementa uma arquitetura "
        "de multi-agentes usando pydantic-ai + OpenRouterModel para resolver um business case real.\n\n"
        "## REGRAS DO CÓDIGO GERADO\n"
        "1. Use SEMPRE: from pydantic_ai import Agent; from pydantic_ai.models.openrouter import OpenRouterModel\n"
        "2. Use o modelo: OpenRouterModel('openai/gpt-4o-mini')\n"
        "3. Cada agente deve ter system_prompt claro e específico para sua função\n"
        "4. O código deve ser 100% executável com: python arquivo.py\n"
        "5. Use run_sync() para execução síncrona\n"
        "6. Simule ferramentas com funções Python simples (não use APIs reais)\n"
        "7. Imprima logs intermediários de cada agente com print()\n"
        "8. O output final deve ser o resultado da resolução do business case em markdown\n"
        "9. Inclua load_dotenv() e from dotenv import load_dotenv no início\n"
        "10. NÃO use asyncio — use apenas run_sync()\n"
        "11. O código deve demonstrar claramente o padrão arquitetural escolhido\n\n"
        "## ESTRUTURA ESPERADA DO OUTPUT\n"
        "- codigo_python: o código Python completo, sem blocos markdown, sem ```python\n"
        "- descricao_implementacao: explicação em 2-3 frases do que o código faz\n\n"
        "Responda em português. Seja direto e técnico."
    ),
)

# ── Streamlit UI ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Arquiteto de Agentes IA",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background-color: #0a0a0f;
    color: #e8e8e0;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f0c040 0%, #e07b20 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    color: #888;
    font-size: 1rem;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 2rem;
    letter-spacing: 0.05em;
}

.arq-card {
    background: #12121a;
    border: 1px solid #2a2a3a;
    border-left: 4px solid #f0c040;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}

.arq-card.selected {
    border-left: 4px solid #c080ff;
    border-color: #6040a0;
}

.arq-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0c040;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}

.descricao {
    color: #c0c0b8;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.agente-box {
    background: #1a1a26;
    border: 1px solid #2a2a3a;
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
}

.agente-nome {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    color: #7dd4b0;
    font-size: 0.95rem;
    margin-bottom: 0.3rem;
}

.agente-funcao {
    color: #a0a09a;
    font-size: 0.87rem;
    margin-bottom: 0.4rem;
}

.ferramenta-tag {
    display: inline-block;
    background: #1e2a22;
    border: 1px solid #3a5a44;
    color: #7dd4b0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px 3px 2px 0;
}

.vantagem {
    color: #7dd4b0;
    font-size: 0.87rem;
    padding: 2px 0;
}

.desvantagem {
    color: #e07060;
    font-size: 0.87rem;
    padding: 2px 0;
}

.rec-card {
    background: linear-gradient(135deg, #1a1420 0%, #12121a 100%);
    border: 1px solid #6040a0;
    border-left: 4px solid #c080ff;
    border-radius: 8px;
    padding: 1.8rem;
    margin-top: 1rem;
}

.rec-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.2rem;
    color: #c080ff;
    margin-bottom: 0.8rem;
}

.rec-text {
    color: #d0c8e0;
    font-size: 0.95rem;
    line-height: 1.7;
}

.resultado-card {
    background: #0d1a12;
    border: 1px solid #1a4a2a;
    border-left: 4px solid #40c080;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
}

.resultado-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    color: #40c080;
    margin-bottom: 1rem;
}

.stTextArea textarea {
    background-color: #12121a !important;
    border: 1px solid #2a2a3a !important;
    color: #e8e8e0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    border-radius: 6px !important;
}

.stTextArea textarea:focus {
    border-color: #f0c040 !important;
    box-shadow: 0 0 0 2px rgba(240,192,64,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #f0c040, #e07b20) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.6rem 2.5rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}

div[data-testid="stHorizontalBlock"] .stButton > button {
    background: #1a1a26 !important;
    color: #c080ff !important;
    border: 1px solid #6040a0 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 1.2rem !important;
}

div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: #2a1a3a !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────────

if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "arquitetura_selecionada" not in st.session_state:
    st.session_state.arquitetura_selecionada = None
if "codigo_gerado" not in st.session_state:
    st.session_state.codigo_gerado = None
if "resultado_execucao" not in st.session_state:
    st.session_state.resultado_execucao = None
if "business_case" not in st.session_state:
    st.session_state.business_case = ""

# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">🧠 Arquiteto de Agentes</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// analise seu business case em 4 arquiteturas de multi-agentes</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────

business_case = st.text_area(
    "Descreva seu business case:",
    placeholder="Ex: Quero automatizar o atendimento ao cliente de um e-commerce, triando dúvidas, consultando pedidos e escalando para humanos quando necessário...",
    height=150,
    label_visibility="collapsed",
    value=st.session_state.business_case,
)

col1, col2 = st.columns([1, 5])
with col1:
    analisar = st.button("Analisar →")

# ── Helpers de renderização ────────────────────────────────────────────────────

def render_arquitetura(titulo: str, arq: ArquiteturaDetalhe, chave: str):
    agentes_html = ""
    for agente in arq.agentes:
        tags = "".join(
            f'<span class="ferramenta-tag">{f}</span>'
            for f in agente.ferramentas
        )
        agentes_html += (
            '<div class="agente-box">'
            f'<div class="agente-nome">⬡ {agente.nome}</div>'
            f'<div class="agente-funcao">{agente.funcao}</div>'
            f'<div>{tags}</div>'
            '</div>'
        )

    vantagens_html = "".join(f'<div class="vantagem">✓ {v}</div>' for v in arq.vantagens)
    desvantagens_html = "".join(f'<div class="desvantagem">✗ {d}</div>' for d in arq.desvantagens)

    selecionada = st.session_state.arquitetura_selecionada == chave
    card_class = "arq-card selected" if selecionada else "arq-card"

    html = (
        f'<div class="{card_class}">'
        f'<div class="arq-title">{titulo}</div>'
        f'<div class="descricao">{arq.descricao_geral}</div>'
        '<div class="section-label">agentes</div>'
        f'{agentes_html}'
        '<div style="display:flex;gap:2rem;margin-top:1rem;">'
        '<div style="flex:1"><div class="section-label">vantagens</div>'
        f'{vantagens_html}</div>'
        '<div style="flex:1"><div class="section-label">desvantagens</div>'
        f'{desvantagens_html}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

    label = "✓ Selecionada" if selecionada else "⚙ Implementar esta arquitetura"
    if st.button(label, key=f"btn_{chave}", disabled=selecionada):
        st.session_state.arquitetura_selecionada = chave
        st.session_state.codigo_gerado = None
        st.session_state.resultado_execucao = None
        st.rerun()

# ── Execução principal ─────────────────────────────────────────────────────────

if analisar:
    if not business_case.strip():
        st.warning("⚠️ Descreva um business case antes de analisar.")
    else:
        st.session_state.business_case = business_case
        st.session_state.arquitetura_selecionada = None
        st.session_state.codigo_gerado = None
        st.session_state.resultado_execucao = None
        with st.spinner("Analisando arquiteturas... aguarde."):
            resposta = agente_arquiteto.run_sync(business_case)
            st.session_state.resultado = resposta.output
        st.rerun()

# ── Exibe resultados da análise ────────────────────────────────────────────────

if st.session_state.resultado:
    resultado = st.session_state.resultado
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        render_arquitetura("① Prompt Chaining",  resultado.arquitetura_1_prompt_chaining,  "arq1")
        render_arquitetura("③ Parallelization",   resultado.arquitetura_3_parallelization,   "arq3")
    with col_b:
        render_arquitetura("② Orchestrator-Workers", resultado.arquitetura_2_orchestrator_workers, "arq2")
        render_arquitetura("④ Routing",              resultado.arquitetura_4_routing,              "arq4")

    rec_html = (
        '<div class="rec-card">'
        '<div class="rec-title">⭐ Recomendação do Arquiteto</div>'
        f'<div class="rec-text">{resultado.recomendacao_final}</div>'
        '</div>'
    )
    st.markdown(rec_html, unsafe_allow_html=True)

# ── Geração de código ──────────────────────────────────────────────────────────

ARQ_LABELS = {
    "arq1": "Prompt Chaining",
    "arq2": "Orchestrator-Workers",
    "arq3": "Parallelization",
    "arq4": "Routing",
}

ARQ_OBJETOS = {
    "arq1": lambda r: r.arquitetura_1_prompt_chaining,
    "arq2": lambda r: r.arquitetura_2_orchestrator_workers,
    "arq3": lambda r: r.arquitetura_3_parallelization,
    "arq4": lambda r: r.arquitetura_4_routing,
}

if st.session_state.arquitetura_selecionada and st.session_state.resultado:
    chave = st.session_state.arquitetura_selecionada
    label = ARQ_LABELS[chave]
    arq_obj = ARQ_OBJETOS[chave](st.session_state.resultado)
    business_case_salvo = st.session_state.business_case

    st.divider()
    st.markdown(
        f'<div class="rec-title" style="color:#f0c040;font-family:Syne,sans-serif;font-weight:800;font-size:1.3rem;">⚙ Implementação — {label}</div>',
        unsafe_allow_html=True
    )

    if st.session_state.codigo_gerado is None:
        prompt_geracao = (
            f"Business case: {business_case_salvo}\n\n"
            f"Arquitetura escolhida: {label}\n\n"
            f"Descrição: {arq_obj.descricao_geral}\n\n"
            f"Agentes:\n"
            + "\n".join(
                f"- {a.nome}: {a.funcao} | ferramentas: {', '.join(a.ferramentas)}"
                for a in arq_obj.agentes
            )
        )
        with st.spinner(f"Gerando código para arquitetura {label}..."):
            resposta_codigo = agente_gerador.run_sync(prompt_geracao)
            st.session_state.codigo_gerado = resposta_codigo.output

    codigo = st.session_state.codigo_gerado

    st.markdown(
        f'<div style="color:#a0a09a;font-size:0.9rem;margin:0.5rem 0 1rem 0;">{codigo.descricao_implementacao}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-label" style="margin-bottom:0.3rem;">código gerado</div>', unsafe_allow_html=True)
    st.code(codigo.codigo_python, language="python")

    col_exec1, col_exec2 = st.columns([1, 5])
    with col_exec1:
        executar = st.button("▶ Executar código")

    if executar:
        st.session_state.resultado_execucao = None
        with st.spinner("Executando agentes... aguarde."):
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8"
            ) as tmp:
                tmp.write(codigo.codigo_python)
                tmp_path = tmp.name

            try:
                proc = subprocess.run(
                    [sys.executable, tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={**os.environ},
                )
                stdout = proc.stdout.strip()
                stderr = proc.stderr.strip()

                if proc.returncode == 0:
                    st.session_state.resultado_execucao = {
                        "sucesso": True,
                        "output": stdout,
                    }
                else:
                    st.session_state.resultado_execucao = {
                        "sucesso": False,
                        "output": stdout,
                        "erro": stderr,
                    }
            except subprocess.TimeoutExpired:
                st.session_state.resultado_execucao = {
                    "sucesso": False,
                    "output": "",
                    "erro": "⏱ Timeout: execução excedeu 120 segundos.",
                }
            finally:
                os.unlink(tmp_path)

# ── Exibe resultado da execução ────────────────────────────────────────────────

if st.session_state.resultado_execucao:
    exec_res = st.session_state.resultado_execucao

    if exec_res["sucesso"]:
        st.markdown(
            '<div class="resultado-card">'
            '<div class="resultado-title">✅ Resultado da Execução</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(exec_res["output"])
    else:
        st.markdown(
            '<div style="background:#1a0d0d;border:1px solid #4a1a1a;border-left:4px solid #e04040;'
            'border-radius:8px;padding:1.5rem;margin-top:1rem;">'
            '<div style="color:#e04040;font-family:Syne,sans-serif;font-weight:800;font-size:1.1rem;margin-bottom:0.8rem;">'
            '❌ Erro na Execução</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if exec_res.get("output"):
            st.markdown("**Output capturado:**")
            st.markdown(exec_res["output"])
        if exec_res.get("erro"):
            st.markdown("**Traceback:**")
            st.code(exec_res["erro"], language="bash")