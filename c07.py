import requests

def pesquisar_wikipedia(termo: str) -> str:
    """
    Pesquisa informações sobre um tema na Wikipedia em português.
    Use quando precisar de informações factuais sobre qualquer assunto.
    """
    # Passo 1: busca o título certo
    busca = requests.get(
        "https://pt.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": termo,
            "format": "json",
            "srlimit": 1,
        },
        timeout=5,
    )
    resultados = busca.json().get("query", {}).get("search", [])
    if not resultados:
        return f"Não encontrei nada sobre '{termo}'."

    titulo = resultados[0]["title"]  # título real do artigo

    # Passo 2: busca o resumo com o título certo
    resumo = requests.get(
        f"https://pt.wikipedia.org/api/rest_v1/page/summary/{titulo.replace(' ', '_')}",
        timeout=5,
    )
    if resumo.status_code != 200:
        return f"Não consegui carregar o artigo '{titulo}'."

    texto = resumo.json().get("extract", "Sem resumo.")
    return f"[Artigo: {titulo}]\n{texto}"