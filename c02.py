from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel


load_dotenv()


# Instrução vaga — o agente não tem identidade clara
agente_vago = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    system_prompt="Você é um assistente inteligente.",
)


# Instrução focada — o agente tem uma responsabilidade única
agente_focado = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    system_prompt=(
        "Você analisa textos científicos e extrai as conclusões principais. "
        "Entenda o conceito central e faça reflexões técnicas da área "
        "Seja objetivo e preciso. Use linguagem técnica adequada. "
        "Não opine sobre o mérito da pesquisa - traga conceitos consolidados conhecidos para agregar na análise "
        "Se o texto não for científico, diga isso claramente."
    ),
)


texto = """
Pesquisadores da USP identificaram que a exposição prolongada a telas
antes de dormir reduz em 40% a produção de melatonina, hormônio
responsável pela regulação do sono. O estudo acompanhou 200 voluntários
por 6 meses e concluiu que o uso de filtros de luz azul não elimina
completamente o problema.
"""


r1 = agente_vago.run_sync(f"Analise: {texto}")
r2 = agente_focado.run_sync(f"Analise: {texto}")


print("VAGO:")
print(r1.output)
print("\nFOCADO:")
print(r2.output)
