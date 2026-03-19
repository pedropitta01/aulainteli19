# pip3 install pydantic-ai requests python-dotenv



from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel


load_dotenv()


# Modelo mais barato e rápido — bom para tarefas simples
agente_mini = Agent(model=OpenRouterModel("xiaomi/mimo-v2-omni"))


# Modelo mais capaz — melhor para raciocínio complexo
agente_full = Agent(model=OpenRouterModel("xiaomi/mimo-v2-pro"))


# Você pode misturar modelos no mesmo sistema:
# usar o barato para triagem e o caro para análise profunda
r = agente_mini.run_sync("Qual a capital do Brasil?")
print(r.output)
print(f"Chamadas: {r.usage().requests}")
# requests=1 — foi uma vez e respondeu direto
# Isso ainda não é um agente — só um LLM respondendo