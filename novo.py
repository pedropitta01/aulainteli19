import streamlit as st
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic import BaseModel
from typing import List

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
</style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown('<div class="hero-title">🧠 Arquiteto de Agentes</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">// analise seu business case em 4 arquiteturas de multi-agentes</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────

business_case = st.text_area(
    "Descreva seu business case:",
    placeholder="Ex: Quero automatizar o atendimento ao cliente de um e-commerce, triando dúvidas, consultando pedidos e escalando para humanos quando necessário...",
    height=150,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 5])
with col1:
    analisar = st.button("Analisar →")

# ── Helpers de renderização ────────────────────────────────────────────────────

def render_arquitetura(titulo: str, arq: ArquiteturaDetalhe):
    ferramentas_html = ""
    agentes_html = ""
    for agente in arq.agentes:
        tags = "".join(f'<span class="ferramenta-tag">{f}</span>' for f in agente.ferramentas)
        agentes_html += f"""
        <div class="agente-box">
            <div class="agente-nome">⬡ {agente.nome}</div>
            <div class="agente-funcao">{agente.funcao}</div>
            <div>{tags}</div>
        </div>
        """

    vantagens_html = "".join(f'<div class="vantagem">✓ {v}</div>' for v in arq.vantagens)
    desvantagens_html = "".join(f'<div class="desvantagem">✗ {d}</div>' for d in arq.desvantagens)

    st.markdown(f"""
    <div class="arq-card">
        <div class="arq-title">{titulo}</div>
        <div class="descricao">{arq.descricao_geral}</div>
        <div class="section-label">agentes</div>
        {agentes_html}
        <div style="display:flex; gap:2rem; margin-top:1rem;">
            <div style="flex:1">
                <div class="section-label">vantagens</div>
                {vantagens_html}
            </div>
            <div style="flex:1">
                <div class="section-label">desvantagens</div>
                {desvantagens_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Execução ───────────────────────────────────────────────────────────────────

if analisar:
    if not business_case.strip():
        st.warning("⚠️ Descreva um business case antes de analisar.")
    else:
        with st.spinner("Analisando arquiteturas... aguarde."):
            resposta = agente_arquiteto.run_sync(business_case)
            resultado = resposta.output

        st.divider()

        col_a, col_b = st.columns(2)

        with col_a:
            render_arquitetura("① Prompt Chaining",       resultado.arquitetura_1_prompt_chaining)
            render_arquitetura("③ Parallelization",       resultado.arquitetura_3_parallelization)

        with col_b:
            render_arquitetura("② Orchestrator-Workers",  resultado.arquitetura_2_orchestrator_workers)
            render_arquitetura("④ Routing",               resultado.arquitetura_4_routing)

        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-title">⭐ Recomendação do Arquiteto</div>
            <div class="rec-text">{resultado.recomendacao_final}</div>
        </div>
        """, unsafe_allow_html=True)

        st.caption(f"📊 Chamadas à API: {resposta.usage().requests}")