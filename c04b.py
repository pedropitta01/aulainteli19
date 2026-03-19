# -*- coding: utf-8 -*-
import os
import re
import json
import html
import csv
import unicodedata
from math import log
from typing import List, Dict, Optional
from collections import defaultdict

import requests
from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel

# -----------------------------------------------------------------------------
# Configuração base
# -----------------------------------------------------------------------------
load_dotenv()

HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "AgenteGastronomia/1.2 (demo multi-ferramentas)")
}

CONTADOR = {"n": 0}


def _tool_log(nome: str):
    CONTADOR["n"] += 1
    print(f"  [Tool call #{CONTADOR['n']}] {nome}...")


# -----------------------------------------------------------------------------
# FERRAMENTA 1 — MICHELIN (São Paulo)
# -----------------------------------------------------------------------------
def buscar_michelin_sp() -> str:
    """
    Retorna HTML/texto de páginas do Guia MICHELIN para São Paulo.
    O agente (LLM) extrai as infos (2★, 1★, Bib Gourmand, Recomendados).
    """
    _tool_log("MICHELIN SP")
    urls = [
        # Cidade (EN/PT)
        "https://guide.michelin.com/en/br/sao-paulo-region/sao-paulo/restaurants",
        "https://guide.michelin.com/br/pt_BR/sao-paulo-region/sao-paulo/restaurants",
        # Editorial com todos estrelados em SP
        "https://guide.michelin.com/en/article/dining-out/all-michelin-starred-restaurants-in-sao-paulo",
    ]
    blobs = []
    for u in urls:
        try:
            r = requests.get(u, timeout=10, headers=HEADERS)
            if r.ok:
                blobs.append(f"[{u}]\n{r.text[:120000]}")
        except Exception as e:
            blobs.append(f"[{u}] ERRO: {e}")
    return "\n\n".join(blobs) if blobs else "[MICHELIN] Sem dados."


# -----------------------------------------------------------------------------
# FERRAMENTA 2 — Latin America’s 50 Best Restaurants (2025)
# -----------------------------------------------------------------------------
def buscar_50best_latam_2025() -> str:
    """
    Busca páginas da lista 2025 da Latin America's 50 Best (e perfis de SP).
    O agente cruza posições e prêmios (ex.: Tuju #8/Melhor do Brasil 2025).
    """
    _tool_log("50 Best LatAm 2025")
    urls = [
        "https://www.theworlds50best.com/latinamerica/en/",
        "https://www.theworlds50best.com/latinamerica/en/the-list/tuju.html",
        "https://www.theworlds50best.com/latinamerica/en/the-list/nelita.html",
        "https://www.theworlds50best.com/latinamerica/en/the-list/a-casa-do-porco.html",
        # Discovery do Evvai (cita posição/premiações na LatAm 2025)
        "https://www.theworlds50best.com/discovery/Establishments/Brazil/S%C3%A3o-Paulo/Evvai.html",
    ]
    blobs = []
    for u in urls:
        try:
            r = requests.get(u, timeout=10, headers=HEADERS)
            if r.ok:
                blobs.append(f"[{u}]\n{r.text[:120000]}")
        except Exception as e:
            blobs.append(f"[{u}] ERRO: {e}")
    return "\n\n".join(blobs) if blobs else "[50BEST] Sem dados."


# -----------------------------------------------------------------------------
# FERRAMENTA 3 — VEJA SP (Comer & Beber 2025)
# -----------------------------------------------------------------------------
def buscar_veja_sp_comer_beber_2025() -> str:
    """
    Retorna página de vencedores do VEJA COMER & BEBER 2025 (São Paulo),
    como sinal de curadoria local (categorias e prêmios).
    """
    _tool_log("VEJA SP Comer & Beber 2025")
    url = "https://vejasp.abril.com.br/coluna/arnaldo-lorencato/comer-e-beber-2025-melhores-restaurantes-sao-paulo/"
    try:
        r = requests.get(url, timeout=10, headers=HEADERS)
        return f"[{url}]\n{r.text[:120000]}" if r.ok else f"[VEJA] Falha {r.status_code}"
    except Exception as e:
        return f"[VEJA] Erro: {e}"


# -----------------------------------------------------------------------------
# FERRAMENTA 4 — Tripadvisor (sinal de popularidade)
# -----------------------------------------------------------------------------
def buscar_tripadvisor_sp_top() -> str:
    """
    Busca índice de 'Melhores restaurantes' em São Paulo (Tripadvisor),
    para sinal de popularidade (rating/volume).
    """
    _tool_log("Tripadvisor SP")
    urls = [
        "https://www.tripadvisor.com.br/Restaurants-g303631-Sao_Paulo_State_of_Sao_Paulo.html",
        "https://www.tripadvisor.com/Restaurants-g303631-Sao_Paulo_State_of_Sao_Paulo.html",
    ]
    blobs = []
    for u in urls:
        try:
            r = requests.get(u, timeout=10, headers=HEADERS)
            if r.ok:
                blobs.append(f"[{u}]\n{r.text[:120000]}")
        except Exception as e:
            blobs.append(f"[{u}] ERRO: {e}")
    return "\n\n".join(blobs) if blobs else "[TRIP] Sem dados."


# -----------------------------------------------------------------------------
# FERRAMENTA 5 — Google Places (opcional)
# -----------------------------------------------------------------------------
def buscar_google_places(consulta: str, cidade: str = "São Paulo") -> str:
    """
    (Opcional) Usa Google Places Text Search se GOOGLE_MAPS_API_KEY estiver definido.
    Retorna JSON com name, rating, votes, price_level e address.
    """
    _tool_log(f"Google Places: '{consulta}' em {cidade}")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "[GPlaces] Sem API key configurada. Ignorando."
    try:
        q = f"{consulta} restaurant in {cidade}"
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/textsearch/json",
            params={"query": q, "key": api_key, "language": "pt-BR", "region": "br"},
            timeout=10, headers=HEADERS
        )
        data = resp.json()
        itens = []
        for it in data.get("results", [])[:12]:
            itens.append({
                "name": it.get("name"),
                "rating": it.get("rating"),
                "votes": it.get("user_ratings_total"),
                "price_level": it.get("price_level"),
                "address": it.get("formatted_address"),
                "place_id": it.get("place_id"),
            })
        return "[GPlaces]\n" + json.dumps(itens, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[GPlaces] Erro: {e}"


# -----------------------------------------------------------------------------
# Utilidades — Normalização e Resolução de Entidades (deduplicação)
# -----------------------------------------------------------------------------
_STOPWORDS = {
    "restaurante", "restaurant", "ristorante", "cozinha", "bar", "bistrô", "bistro",
    "trattoria", "sushi", "steakhouse", "churrascaria", "gastronomia", "cucina"
}
_BAIRROS_HINTS = [
    "jardins", "jardim paulistano", "itaim", "itaim bibi", "pinheiros", "moema",
    "higienópolis", "perdizes", "vila madalena", "vila olímpia", "paraíso",
    "vila nova conceição", "consolação", "centro"
]

def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))

def normalizar_brand(nome: str) -> str:
    s = _strip_accents((nome or "").lower())
    s = s.replace(" - ", " ").replace("—", " ").replace("-", " ").replace("|", " ")
    tokens = [t for t in re.split(r"\s+", s) if t and t not in _STOPWORDS]
    tokens = [t for t in tokens if t not in _BAIRROS_HINTS]
    s = " ".join(tokens)
    s = re.sub(r"\b(unidade|filial|shopping|mall)\b.*$", "", s).strip()
    s = re.sub(r"\s{2,}", " ", s)
    return s

def extrair_bairro(texto: str) -> Optional[str]:
    s = _strip_accents((texto or "").lower())
    for b in _BAIRROS_HINTS:
        if b in s:
            return b
    return None

def resolver_entidades(items: List[Dict]) -> List[Dict]:
    """
    Une duplicatas por marca/unidade e mantém 1 registro representativo.
    Prioriza: URL MICHELIN > URL 50Best > place_id > brand+bairro > brand.
    Critério de escolha entre múltiplas unidades: maior prestígio + mais fontes + popularidade.
    """
    # 1) agrupa por chave canônica
    grupos = defaultdict(list)
    for it in items:
        brand = normalizar_brand(it.get("name", ""))
        urls = it.get("urls") or {}
        michelin_url = urls.get("michelin")
        fifty_url = urls.get("50best")
        place_id = (it.get("sources", {}).get("places") or {}).get("place_id")
        bairro = it.get("neighborhood") or extrair_bairro(it.get("address", "")) or extrair_bairro(it.get("name", ""))

        if michelin_url:
            key = f"MICHELIN::{michelin_url}"
        elif fifty_url:
            key = f"50BEST::{fifty_url}"
        elif place_id:
            key = f"PLACE::{place_id}"
        elif bairro:
            key = f"BRAND_BAIRRO::{brand}::{bairro}"
        else:
            key = f"BRAND::{brand}"

        it["_brand_norm"] = brand
        it["_bairro_norm"] = bairro
        grupos[key].append(it)

    # 2) por brand, selecionar melhor key (composite score)
    brand_to_keys = defaultdict(list)
    for k, lst in grupos.items():
        if lst:
            brand_to_keys[lst[0]["_brand_norm"]].append(k)

    resultado = []
    for brand, keys in brand_to_keys.items():
        if len(keys) == 1:
            resultado.extend(grupos[keys[0]])
            continue
        melhor_key, melhor_val = None, -1
        for k in keys:
            score_prestigio = 0
            fontes = set()
            rating = 0.0
            votes = 0
            for it in grupos[k]:
                score_prestigio = max(score_prestigio, it.get("score_prestigio", 0))
                for fonte, payload in (it.get("sources") or {}).items():
                    if payload:
                        fontes.add(fonte)
                rating = max(rating, float((it.get("rating") or 0)))
                votes = max(votes, int((it.get("votes") or 0)))
            composite = score_prestigio + 5 * len(fontes) + (rating * (1 + log(votes + 1)))
            if composite > melhor_val:
                melhor_val, melhor_key = composite, k

        # compacta itens da melhor key num único registro
        principal = grupos[melhor_key][0].copy()
        for it in grupos[melhor_key][1:]:
            for fonte, payload in (it.get("sources") or {}).items():
                principal.setdefault("sources", {}).setdefault(fonte, payload)
            for fonte, url in (it.get("urls") or {}).items():
                principal.setdefault("urls", {}).setdefault(fonte, url)
        resultado.append(principal)

    # 3) último filtro para possíveis ecos
    dedup, seen = [], set()
    for it in resultado:
        bn = it["_brand_norm"]
        if bn in seen:
            continue
        seen.add(bn)
        dedup.append(it)
    return dedup


# -----------------------------------------------------------------------------
# Scoring — pontuação de prestígio e composição final
# -----------------------------------------------------------------------------
def pontuar_prestigio(item: Dict) -> int:
    """
    Heurística simples:
        2★ = 100 ; 1★ = 70 ; Bib = 40 ; Recomendado = 20
        50 Best LatAm: top10 = 80; 11-20 = 60; 21-50 = 50
        Vencedor/Top VEJA (se sinalizado) = +10
    """
    s = 0
    mic = (item.get("sources") or {}).get("michelin") or {}
    stars = mic.get("stars")  # 2, 1 ou 0
    if stars == 2:
        s += 100
    elif stars == 1:
        s += 70
    elif mic.get("bib_gourmand"):
        s += 40
    elif mic.get("recommended"):
        s += 20

    fifty = (item.get("sources") or {}).get("fiftybest") or {}
    rank = fifty.get("latam_rank")
    if isinstance(rank, int):
        if 1 <= rank <= 10:
            s += 80
        elif 11 <= rank <= 20:
            s += 60
        elif 21 <= rank <= 50:
            s += 50

    veja = (item.get("sources") or {}).get("veja") or {}
    if veja.get("award"):
        s += 10

    return s


def compor_final(items: List[Dict], top_n: int = 10) -> List[Dict]:
    # 1) pontua
    for it in items:
        it["score_prestigio"] = pontuar_prestigio(it)
    # 2) dedup (por marca/unidade)
    itens_dedup = resolver_entidades(items)
    # 3) ordenar por score + popularidade
    for it in itens_dedup:
        rating = float(it.get("rating") or 0)
        votes = int(it.get("votes") or 0)
        it["_comp_score"] = it["score_prestigio"] + (rating * (1 + log(votes + 1)))
    itens_dedup.sort(key=lambda x: x["_comp_score"], reverse=True)
    return itens_dedup[:top_n]


# -----------------------------------------------------------------------------
# Agente ReAct
# -----------------------------------------------------------------------------
agente = Agent(
    model=OpenRouterModel("xiaomi/mimo-v2-pro"),
    tools=[buscar_michelin_sp, buscar_50best_latam_2025, buscar_veja_sp_comer_beber_2025, buscar_tripadvisor_sp_top, buscar_google_places],
    system_prompt=(
        "Você é um agente gastronômico de São Paulo que usa MÚLTIPLAS FONTES. "
        "SEM Wikipedia. "
        "Obrigatório consultar ao menos MICHELIN e 50 Best. Use VEJA SP como curadoria local; "
        "Tripadvisor como popularidade; e Google Places (se disponível) como rating extra. "
        "RETORNE ESTRUTURADO EM JSON (e somente JSON), com a seguinte estrutura:\n"
        "{ 'items':[{\n"
        "  'name': str,\n"
        "  'neighborhood': str|None,\n"
        "  'address': str|None,\n"
        "  'urls': {'michelin': str|None, '50best': str|None, 'site': str|None},\n"
        "  'sources': {\n"
        "     'michelin': {'stars': 0|1|2, 'bib_gourmand': bool, 'recommended': bool} | None,\n"
        "     'fiftybest': {'latam_rank': int|None, 'note': str|None} | None,\n"
        "     'veja': {'award': str|None} | None,\n"
        "     'trip': {'rating': float|None, 'votes': int|None} | None,\n"
        "     'places': {'rating': float|None, 'votes': int|None, 'place_id': str|None} | None\n"
        "  }\n"
        "}]}\n"
        "Incluir SOMENTE restaurantes na cidade de São Paulo (capital). "
        "Preencher o que souber com base nas páginas coletadas; campos desconhecidos podem ser null. "
        "Evite duplicar marcas com unidades diferentes (mas pode listar mais de um se forem propostas distintas)."
    ),
)


# -----------------------------------------------------------------------------
# Execução e formatação
# -----------------------------------------------------------------------------
def executar(top_n: int = 10, export_csv: bool = True, csv_path: str = "top10_sp.csv"):
    print("=" * 90)
    print("Agente ReAct — Melhores restaurantes de São Paulo (consenso multi-fontes)")
    print("=" * 90)

    pergunta = (
        "Monte uma lista de candidatos a 'melhores restaurantes de São Paulo'. "
        "Consulte: MICHELIN (2★, 1★, Bib, recomendados), Latin America's 50 Best (2025), "
        "VEJA COMER & BEBER 2025, Tripadvisor e, se possível, Google Places. "
        "Retorne somente JSON conforme o schema instruído."
    )

    # 1) roda o agente e tenta interpretar JSON
    result = agente.run_sync(pergunta)
    raw = result.output

    data = {}
    try:
        data = json.loads(raw)
        assert isinstance(data, dict) and "items" in data
    except Exception:
        # fallback: tenta extrair bloco JSON se o modelo tiver cercado com crases
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                data = json.loads(m.group(0))
            except Exception:
                pass

    if not data or "items" not in data:
        print("\n[ERRO] O agente não retornou JSON válido. Conteúdo recebido:\n")
        print(raw[:2000])
        return

    items = data["items"]

    # 2) normaliza campos e carrega sinais de popularidade em nível raiz
    norm_items = []
    for it in items:
        name = it.get("name") or ""
        neighborhood = it.get("neighborhood")
        address = it.get("address")
        urls = it.get("urls") or {}
        sources = it.get("sources") or {}
        # extrai sinais (preferir Google Places; senão Trip)
        rating = None
        votes = None
        if sources.get("places", {}):
            rating = sources["places"].get("rating")
            votes = sources["places"].get("votes")
        if (rating is None or votes is None) and sources.get("trip", {}):
            rating = rating or sources["trip"].get("rating")
            votes = votes or sources["trip"].get("votes")

        norm_items.append({
            "name": name,
            "neighborhood": neighborhood,
            "address": address,
            "urls": urls,
            "sources": sources,
            "rating": rating,
            "votes": votes
        })

    # 3) compor final (pontuação + dedup + ordenação)
    top = compor_final(norm_items, top_n=top_n)

    # 4) imprimir resultado
    print("\nTOP {} — consenso (prestígio + popularidade):\n".format(top_n))
    for i, it in enumerate(top, 1):
        mic = (it.get("sources") or {}).get("michelin") or {}
        stars = mic.get("stars")
        bib = mic.get("bib_gourmand")
        rec = mic.get("recommended")
        tags = []
        if stars == 2:
            tags.append("2★ MICHELIN")
        elif stars == 1:
            tags.append("1★ MICHELIN")
        if bib:
            tags.append("Bib Gourmand")
        if rec and not stars and not bib:
            tags.append("Recomendado MICHELIN")

        fifty = (it.get("sources") or {}).get("fiftybest") or {}
        if isinstance(fifty.get("latam_rank"), int):
            tags.append(f"50 Best LatAm #{fifty['latam_rank']}")

        veja = (it.get("sources") or {}).get("veja") or {}
        if veja.get("award"):
            tags.append(f"VEJA: {veja['award']}")

        nota_pop = ""
        if it.get("rating"):
            nota_pop = f" — Popularidade: {it['rating']:.1f}★ ({it.get('votes',0)} avaliações)"

        linha = f"{i:02d}. {it['name']}"
        if it.get("neighborhood"):
            linha += f" ({it['neighborhood']})"
        if tags:
            linha += " — " + " · ".join(tags)
        linha += nota_pop
        print(linha)

        # fontes
        urls = it.get("urls") or {}
        fontes = []
        if urls.get("michelin"): fontes.append(f"MICHELIN: {urls['michelin']}")
        if urls.get("50best"):   fontes.append(f"50 Best: {urls['50best']}")
        if urls.get("site"):     fontes.append(f"Site: {urls['site']}")
        if fontes:
            for f in fontes:
                print("     ", f)
        print()

    # 5) exportar CSV (opcional)
    if export_csv:
        campos = [
            "rank","name","neighborhood","address","michelin_stars","michelin_bib",
            "fiftybest_rank","veja_award","rating","votes","michelin_url","fiftybest_url","site_url"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as fp:
            w = csv.DictWriter(fp, fieldnames=campos)
            w.writeheader()
            for i, it in enumerate(top, 1):
                mic = (it.get("sources") or {}).get("michelin") or {}
                fifty = (it.get("sources") or {}).get("fiftybest") or {}
                veja = (it.get("sources") or {}).get("veja") or {}
                urls = it.get("urls") or {}
                w.writerow({
                    "rank": i,
                    "name": it.get("name"),
                    "neighborhood": it.get("neighborhood"),
                    "address": it.get("address"),
                    "michelin_stars": (mic.get("stars") or 0),
                    "michelin_bib": bool(mic.get("bib_gourmand")),
                    "fiftybest_rank": fifty.get("latam_rank"),
                    "veja_award": veja.get("award"),
                    "rating": it.get("rating"),
                    "votes": it.get("votes"),
                    "michelin_url": urls.get("michelin"),
                    "fiftybest_url": urls.get("50best"),
                    "site_url": urls.get("site"),
                })
        print(f"[OK] CSV exportado: {csv_path}")

    # 6) métricas
    try:
        usage = agente.run_sync("ping").usage()  # truque para acessar usage; pode retornar None
    except Exception:
        usage = None
    print(f"\nFerramentas chamadas: {CONTADOR['n']}")
    if usage is not None:
        print(f"Chamadas ao modelo LLM: {usage.requests}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    executar(top_n=10, export_csv=True, csv_path="top10_sp.csv")