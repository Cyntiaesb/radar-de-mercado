"""Esqueleto de um especialista novo, de qualquer nicho. Copiar pra especialistas/<slug>.py e trocar tudo.

Montar: python scripts/monta_painel.py <slug>   (o script avisa qual chave falta)
Exemplo com dados fictícios: especialistas/exemplo.py.

Regras que valem pra todo nicho:
- Número que vem de coleta (views, mediana, anúncios, dias no ar) sai de script, nunca digitado de cabeça.
- O que não foi visto entra como "não visto" / "não coletado", nunca chutado.
- "Leitura nossa" é interpretação; o resto é fato com fonte.
"""
from painel_lib import fichas, ler, reels_ig  # noqa: F401

TITULO = "Mercado de Fulana"
CABECALHO = "Fulana · coletados DD/MM/AAAA"

# Reels: rodar antes scripts/coleta_reels.py e scripts/resumo_reels.py (ver README).
# brutos = ler("<slug>/reels.json"); resumo = ler("<slug>/reels-resumo.json")
# reels, perfis = reels_ig("<slug>", [("@dela", "Fulana", 8), ("@concorrente", "Beltrana", 4)], brutos, resumo)
reels, perfis = [], []

# Anúncios: scripts/coleta_anuncios.py + resumo_anuncios.py. Uma ficha por cartão, na mesma ordem:
# [gancho, promessa, oferta, CTA, consciência, etapa do funil, é lançamento?]
cartoes, F = [], []

D = {
 "data": "DD/MM/AAAA",
 # Quem é. Os pronomes deixam o texto das abas certo pra homem ou mulher ("ele/dele/do/Do/sozinho/exposto").
 "cli": {"id": "cli", "nome": "Fulana de Tal", "curto": "Fulana", "quem": "nome de registro", "at": "@fulana", "seg": "não visto", "yt": "não visto",
         "titulo": "Como se apresenta e o registro profissional achado", "hub": "linktr.ee/...", "cnpj": "razão social · cidade",
         "ela": "ela", "dela": "dela", "da": "da", "Da": "Da", "sozinha": "sozinha", "exposta": "exposta"},
 # Grupos de concorrente do nicho. A chave vai em conc[].grupo; secular=True / ref=True marcam quem entra só como referência.
 "grupos": {"publico": "vendem pro mesmo público", "formacao": "vendem formação"},
 "gruposTitulo": {"publico": "Vendem pro mesmo público", "formacao": "Formação de profissionais"},
 "txt": {
   "h1": "O mercado da <em>profissão dela</em>, aba por aba.",
   "faixaProdutos": "de R$ X a R$ Y",
   "tile4": ["Rótulo do 4º quadro do resumo", "valor", "explicação curta"],
   "mapa": ["← EIXO ESQUERDO", "EIXO DIREITO →", "canto de cima à direita"],
   "legendaMapa": "Eixo vertical: maior preço publicado (escala log). <b style=\"color:var(--verde)\">Verde</b> é a Fulana.",
   "varremosFora": "quantos nomes foram conferidos e ficaram de fora, e onde está a lista",
   "produtosH2": "N produtos, do mais barato ao mais caro",
   "fontesProdutos": ["site", "checkout"],
   "cliProdutoLinha": ["Fulana", "produto principal", "preço", "garantia", "bônus", "escada"],
   "repH2": "O que falam da Fulana na internet", "repFontes": ["Reclame Aqui", "comentários"], "temasLbl": "Do que criticam nos comentários",
   "ytH2": "Onde ela domina, e quem ensina o tema de graça", "ytFontes": ["YouTube · canal dela"], "ytFora": "",
   "ytLeitura": "Leitura nossa: ...",
   "custoReels": "US$ 0,00",
   "reelsRodape": "Como a coleta foi feita e quem ficou sem coletar.",
   "histDe": "da Fulana",
   "agendaLbl": "Agenda pública", "fontesLanc": ["páginas dos eventos"],
   "fontesPublico": ["comentários"], "fontesFunil": ["linktr.ee"],
 },
 # Confiança geral e por achado: "alta", "moderada" ou "baixa" (o quanto a conclusão aguenta, dado o que foi coletado).
 "confianca": ["moderada", "O que sustenta e o que pesa contra, em uma ou duas frases."],
 "achados": [["Achado 1 em uma frase.", "Explicação com número e fonte.", "alta"]],
 "cliPrecos": [["Fulana · produto", 100]],
 "cliLinha": {"maior": "R$ 100", "gar": "7 dias", "escada": "R$ X → R$ Y", "vende": "Reel → página → checkout"},
 "produtos": [{"nome": "Produto", "grupo": "Formato · público", "preco": 100, "txt": "R$ 100 à vista", "fatos": ["fato"], "por": "Como ela descreve", "fonte": "site"}],
 # Concorrentes. x = posição no eixo do mapa (0 a 1), preco_y = maior preço publicado (None = fora do mapa).
 "conc": [{"id": "beltrana", "nome": "Beltrana", "at": "@beltrana", "grupo": "publico", "origem": "Busca", "seg": "nc", "yt": "não visto", "ytn": 0,
           "motivo": "Por que é concorrente (vende produto parecido pro mesmo público).", "promessa": "—", "preco": None, "precoTxt": "não publicado",
           "produto": "—", "garantia": "—", "bonus": "—", "degrau": "—", "funil": ["Reel", "Página"], "fraco": "Onde é fraca.", "x": .5, "preco_y": None}],
 "cliMapa": {"x": .5, "preco_y": 100},
 "espacos": [["Onde ela está sozinha", "Título", "Explicação"], ["Onde ela está exposta", "Título", "Explicação"]],
 "rep": {"tiles": [["Reclame Aqui", "não visto", "—"]], "canais": [["Canal", "resumo", [0, 100, 0]]], "semDado": [], "temas": [],
         "elogios": [], "queixas": [], "leituras": [], "conc": [], "nicho": []},
 "ytKpi": [["Inscritos", "—"]], "ytCanais": [["Fulana", 1]], "ytTop": [], "ytGratis": [],
 "reelsIG": reels, "perfisIG": perfis, "leiturasReels": [],
 "ads": [],  # anúncios de terceiros que usam o nome dela; vazio esconde a subaba
 "quemAnuncia": [{"nome": "Fulana", "cli": True, "total": 0, "ativos": 0, "venc": 0, "longo": 0, "copys": 0, "formatos": "—", "destinos": "—"}],
 "anunciosConc": cartoes, "fichasAds": fichas(cartoes, F),
 "padroesConc": [], "histAds": [], "histObs": "", "adsColeta": "DD/MM/AAAA", "adsSemAnuncio": "",
 "agenda": [], "passado": [], "lancConc": [], "bf": [],
 "busca": [["termo buscado", "primeiros resultados", "posição dela"]], "buscaObs": "", "buscaYt": None,
 "voz": [], "dorCopy": [], "decisao": [], "atrai": [], "repele": [], "objecoes": [],
 "persona": {"texto": "Leitura nossa a partir de ...", "campos": [["Idade", "—"]]},
 "eixos": [["Quem compra", "...", ["a", "b", "c"], "FATO"]],
 "igual": [], "ninguem": [], "naoOlhaTitulo": "Público que ninguém olha", "naoOlha": "",
 "camadas": {"cols": ["Fulana", "Beltrana"], "linhas": [["Critério", ["sim", "nao"]]]},
 "hoje": {"frase": "Como ela se apresenta hoje", "promessas": []},
 # [o que diz, o que se vê, veredito ("Confirmada", "Em parte", "Divergente" ou "Sem lastro"), link da fonte]
 "declarado": [], "valor": [], "fit": [], "sintomas": [], "causas": [], "mecanismo": ["Nome", "Explicação"],
 "limites": ["Cada coisa que não foi vista e pode mudar a leitura, uma por linha."],
 # Opcionais: preço por formato ([formato, quem, produto, preço ou None, link]; quem = cli.nome fica verde)
 # e aba Fontes ([tipo, nome, link, onde foi usada, data ou ""]; tipos em painel_lib.TIPOS_FONTE).
 "precosFormato": [], "fontes": [], "validar": [], "proximos": [],
 "fConteudo": [{"id": "cli", "passos": [["Reel", "—"]], "cols": {"hub": "—", "isca": "—", "captura": "—", "yt": "—", "extra": "—"}, "obs": ""}],
 "fVenda": [{"id": "cli", "passos": [["Página", "—"]], "cols": {"destino": "—", "pagina": "—", "preco": "—", "checkout": "—", "garantia": "—", "recup": "—"}, "obs": ""}],
}
