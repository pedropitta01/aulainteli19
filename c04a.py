import os
import re
import html
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

load_dotenv()

# Ajuste seu user-agent se quiser
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "AulaAgentes/1.1 (exemplo multi-ferramentas)")
}

# Contador para observabilidade das ferramentas
contador = {"n": 0}

# ---------------------------------------------------------
# FERRAMENTA 1 — Wikipedia (pt)
# ---------------------------------------------------------
def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Útil para resumos factuais e contexto histórico.
    """
    contador["n"] += 1
    print(f"  [Tool call #{contador['n']}] Wikipedia: pesquisando '{termo}'...")

    try:
        busca = requests.get(
            "https://pt.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": termo,
                "format": "json",
                "srlimit": 1
            },
            timeout=7, headers=HEADERS,
        )
        busca.raise_for_status()
        resultados = busca.json().get("query", {}).get("search", [])
        if not resultados:
            return f"[Wikipedia] Não encontrei nada sobre '{termo}'."

        titulo = resultados[0]["title"]
        resumo = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/page/summary/{titulo.replace(' ', '_')}",
            timeout=7, headers=HEADERS,
        )
        if resumo.status_code != 200:
            return f"[Wikipedia] Artigo '{titulo}' encontrado, mas o resumo não pôde ser obtido."
        data = resumo.json()
        extract = data.get("extract", "Sem resumo.")
        url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        print(f"  [#{contador['n']} concluído — artigo: {titulo}]")
        return f"[Wikipedia: {titulo}]\n{extract}\nFonte: {url}"
    except Exception as e:
        return f"[Wikipedia] Erro: {e}"

# ---------------------------------------------------------
# FERRAMENTA 2 — Wikidata (metadados do item)
# ---------------------------------------------------------
def buscar_wikidata(titulo_ou_qid: str) -> str:
    """
    Busca metadados no Wikidata para um título de Wikipedia (pt) ou um QID (Qxxxx).
    Retorna: país, liga/competição principal, data de fundação e estádio, se disponíveis.
    """
    contador["n"] += 1
    print(f"  [Tool call #{contador['n']}] Wikidata: consultando '{titulo_ou_qid}'...")

    try:
        # Se vier um QID, usa direto; caso contrário, resolve via tradução de título
        qid = None
        if re.fullmatch(r"Q\d+", titulo_ou_qid.strip(), flags=re.IGNORECASE):
            qid = titulo_ou_qid.strip()
        else:
            # Resolve título ptwiki -> QID
            entity = requests.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbgetentities",
                    "sites": "ptwiki",
                    "titles": titulo_ou_qid,
                    "format": "json"
                },
                timeout=8, headers=HEADERS
            )
            entity.raise_for_status()
            ents = entity.json().get("entities", {})
            if ents:
                qid = next(iter(ents.keys()))
            if not qid or qid == "-1":
                return f"[Wikidata] Não foi possível mapear '{titulo_ou_qid}' para um QID."

        # Puxa claims do QID
        details = requests.get(
            "https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(qid),
            timeout=8, headers=HEADERS
        )
        details.raise_for_status()
        data = details.json()
        ent = data.get("entities", {}).get(qid, {})
        labels = ent.get("labels", {})
        label_pt = labels.get("pt", {}).get("value") or labels.get("en", {}).get("value") or qid

        claims = ent.get("claims", {})
        # P17: país; P571: data de fundação; P115: estádio; P118: liga; P413: posição (para jogador)
        def get_value(prop: str) -> Optional[str]:
            if prop not in claims:
                return None
            mainsnak = claims[prop][0].get("mainsnak", {})
            datav = mainsnak.get("datavalue", {})
            val = datav.get("value")
            if not val:
                return None
            if isinstance(val, dict) and "id" in val:
                # precisamos resolver o rótulo desse id
                subid = val["id"]
                sub = requests.get(
                    f"https://www.wikidata.org/wiki/Special:EntityData/{subid}.json",
                    timeout=8, headers=HEADERS
                )
                if sub.status_code == 200:
                    subent = sub.json().get("entities", {}).get(subid, {})
                    return (subent.get("labels", {}).get("pt", {}) or subent.get("labels", {}).get("en", {})).get("value", subid)
                return subid
            # datas (ex: +1914-01-01T00:00:00Z)
            if isinstance(val, dict) and "time" in val:
                return val["time"].lstrip("+").split("T")[0]
            # string literal
            if isinstance(val, str):
                return val
            return None

        pais = get_value("P17")
        liga = get_value("P118")
        fundacao = get_value("P571")
        estadio = get_value("P115")
        posicao = get_value("P413")

        campos = []
        if pais: campos.append(f"País: {pais}")
        if liga: campos.append(f"Liga principal/afilição: {liga}")
        if fundacao: campos.append(f"Fundação: {fundacao}")
        if estadio: campos.append(f"Estádio: {estadio}")
        if posicao: campos.append(f"Posição (jogador): {posicao}")

        if not campos:
            return f"[Wikidata: {label_pt} ({qid})] Sem metadados relevantes disponíveis."
        return f"[Wikidata: {label_pt} ({qid})]\n" + "\n".join(campos)
    except Exception as e:
        return f"[Wikidata] Erro: {e}"

# ---------------------------------------------------------
# FERRAMENTA 3 — Notícias por RSS (ESPN Brasil / ge.globo)
# ---------------------------------------------------------
RSS_FONTES = {
    "espn": "https://www.espn.com.br/rss/",
    # feeds do ge.globo (exemplos de futebol)
    # página de feeds: https://g1.globo.com/rss/ e https://ge.globo.com/servicos/feeds/
    # um feed geral de futebol:
    "ge": "https://ge.globo.com/dynamo/futebol/rss2.xml",
}

def buscar_noticias_rss(fonte: str, termo: str, max_itens: int = 8) -> str:
    """
    Busca manchetes recentes em RSS e filtra pelo termo (case-insensitive).
    Fontes disponíveis: 'espn', 'ge'.
    """
    contador["n"] += 1
    print(f"  [Tool call #{contador['n']}] RSS: fonte='{fonte}', termo='{termo}'...")

    fonte = fonte.lower().strip()
    if fonte not in RSS_FONTES:
        return f"[RSS] Fonte '{fonte}' não suportada. Use: {', '.join(RSS_FONTES.keys())}"

    try:
        resp = requests.get(RSS_FONTES[fonte], timeout=8, headers=HEADERS)
        resp.raise_for_status()
        xml = resp.text

        # Parse simples via regex (suficiente para demo; em produção use feedparser)
        items = re.findall(r"<item>(.*?)</item>", xml, flags=re.DOTALL | re.IGNORECASE)
        resultados = []
        termo_lower = termo.lower()

        for raw in items:
            title = re.search(r"<title>(.*?)</title>", raw, flags=re.DOTALL | re.IGNORECASE)
            link = re.search(r"<link>(.*?)</link>", raw, flags=re.DOTALL | re.IGNORECASE)
            pubdate = re.search(r"<pubDate>(.*?)</pubDate>", raw, flags=re.DOTALL | re.IGNORECASE)
            if not title:
                continue
            t = html.unescape(re.sub(r"<.*?>", "", title.group(1))).strip()
            if termo_lower in t.lower():
                l = (link.group(1).strip() if link else "").strip()
                d = (pubdate.group(1).strip() if pubdate else "")
                resultados.append(f"- {t} ({d})\n  {l}")
                if len(resultados) >= max_itens:
                    break

        if not resultados:
            return f"[RSS:{fonte}] Nenhuma manchete contendo '{termo}'."
        return f"[RSS:{fonte}] Manchetes contendo '{termo}':\n" + "\n".join(resultados)
    except Exception as e:
        return f"[RSS] Erro: {e}"

# ---------------------------------------------------------
# Criação do agente
# ---------------------------------------------------------
agente = Agent(
    model=OpenRouterModel("openai/gpt-4o-mini"),
    tools=[pesquisar_wikipedia, buscar_wikidata, buscar_noticias_rss],
    system_prompt=(
        "Você é um assistente de pesquisa esportiva. "
        "Para COMPARAÇÕES, pesquise CADA tema separadamente antes de responder. "
        "Use: Wikipedia para contexto histórico, Wikidata para metadados (país, liga, fundação), "
        "e RSS (ESPN/ge) para momento atual/noticiário. "
        "Sempre cite as fontes que você usou (URLs quando possível). "
    ),
)

if __name__ == "__main__":
    print("=" * 70)
    print("Loop ReAct — múltiplas ferramentas (Wikipedia + Wikidata + RSS)")
    print("=" * 70)
    print("Pergunta enviada — observe os tool calls acontecendo:\n")

    pergunta = (
        "Compare Palmeiras e Corinthians: história, títulos relevantes, "
        "características (país, liga, fundação, estádio) e o momento atual no noticiário."
    )

    result = agente.run_sync(pergunta)

    print("\nRESPOSTA FINAL:")
    print(result.output)

    # Nem todos os modelos preenchem usage; proteja seu acesso
    try:
        print(f"\nTool calls executados:    {contador['n']}")
        usage = result.usage()
        if usage is not None:
            print(f"Chamadas ao servidor (LLM): {usage.requests}")
    except Exception:
        pass

    print("""
O modelo decidiu sozinho quais ferramentas usar e em que ordem:
  → Wikipedia para contexto histórico
  → Wikidata para metadados estruturados (país, liga, fundação, estádio)
  → RSS ESPN/ge para manchetes recentes (momento atual)

Isso demonstra o padrão ReAct orquestrando múltiplas tool calls.
""")