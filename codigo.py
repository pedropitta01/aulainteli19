from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

class Orchestrator(Agent):
    system_prompt = "Você é um orquestrador do processo seletivo, deve decidir quais agentes processar com base nas informações do currículo."

class ResumeExtractor(Agent):
    system_prompt = "Você extrai e estrutura as informações de um currículo."

class ProfileAnalyzer(Agent):
    system_prompt = "Você verifica se o perfil do candidato atende aos requisitos da vaga."

class MarketResearcher(Agent):
    system_prompt = "Você pesquisa o mercado para avaliar a pretensão salarial do candidato."

class TechnicalReportGenerator(Agent):
    system_prompt = "Você gera um parecer técnico sobre o candidato."

class BehavioralReportGenerator(Agent):
    system_prompt = "Você gera um parecer comportamental baseado nas soft skills do candidato."

class EmailWriter(Agent):
    system_prompt = "Você redige um email com feedback personalizado para o candidato."

# Inicializa os agentes
orchestrator = Orchestrator(model=OpenRouterModel('openai/gpt-4o-mini'))
resume_extractor = ResumeExtractor(model=OpenRouterModel('openai/gpt-4o-mini'))
profile_analyzer = ProfileAnalyzer(model=OpenRouterModel('openai/gpt-4o-mini'))
market_researcher = MarketResearcher(model=OpenRouterModel('openai/gpt-4o-mini'))
technical_report_generator = TechnicalReportGenerator(model=OpenRouterModel('openai/gpt-4o-mini'))
behavioral_report_generator = BehavioralReportGenerator(model=OpenRouterModel('openai/gpt-4o-mini'))
email_writer = EmailWriter(model=OpenRouterModel('openai/gpt-4o-mini'))

# Funções simuladas para as ferramentas

def simulate_pdf_reader(curriculum):
    return {'nome': 'João', 'experiencia': '5 anos em desenvolvimento', 'cargo_desejado': 'Desenvolvedor', 'salario_desejado': 5000}

def simulate_sql_query(profile):
    return profile['cargo_desejado'] == 'Desenvolvedor' and profile['experiencia'] == '5 anos em desenvolvimento'

def simulate_web_search(salary_expectation):
    return salary_expectation < 6000  # Fazendo uma pesquisa simulada simples

def simulate_ml_model(candidate_info):
    return "Candidato possui as habilidades necessárias."

# Orchestration
curriculum = "path_do_curriculo.pdf"
print("[Orchestrator] Iniciando o processo seletivo...")
info_candidato = simulate_pdf_reader(curriculum)
print(f"[Orchestrator] Informações do Candidato: {info_candidato}")

perfil_valido = simulate_sql_query(info_candidato)
print(f"[Orchestrator] Perfil Válido? {perfil_valido}")

situacao_salario = simulate_web_search(info_candidato['salario_desejado'])
print(f"[Orchestrator] Situação Salarial: {'Aceitável' if situacao_salario else 'Inaceitável'}")

technical_report = simulate_ml_model(info_candidato)
print(f"[Orchestrator] Parecer Técnico: {technical_report}")

behavioral_report = simulate_ml_model(info_candidato)
print(f"[Orchestrator] Parecer Comportamental: {behavioral_report}")

feedback_email = print(f"Prezado {info_candidato['nome']},\n\n" + 
    f"Seu perfil foi {'aprovado' if perfil_valido and situacao_salario else 'rejeitado'}. \n" + 
    f"Parecer Técnico: {technical_report}. \n" + 
    f"Parecer Comportamental: {behavioral_report}. \n\nAtenciosamente,\nEquipe RH")

print(f"[Orchestrator] Feedback para o candidato: {feedback_email}")