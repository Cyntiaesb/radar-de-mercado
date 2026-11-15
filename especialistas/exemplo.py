"""EXEMPLO COM DADOS FICTÍCIOS. Empresa, concorrentes, preços e números foram inventados só para mostrar o painel.

Montar: python scripts/monta_painel.py exemplo

Regras que valem pra todo nicho:
- Número que vem de coleta (views, mediana, anúncios, dias no ar) sai de script, nunca digitado de cabeça.
- O que não foi visto entra como "não visto" / "não coletado", nunca chutado.
- "Leitura nossa" é interpretação; o resto é fato com fonte.
"""
from painel_lib import fichas, ler, reels_ig  # noqa: F401

TITULO = "Exemplo fictício · Ateliê Doce Ofício"
CABECALHO = "Exemplo fictício · dados inventados"

# Reels: rodar antes scripts/coleta_reels.py e scripts/resumo_reels.py (ver README).
# brutos = ler("<slug>/reels.json"); resumo = ler("<slug>/reels-resumo.json")
# reels, perfis = reels_ig("<slug>", [("@dela", "Doce Ofício", 8), ("@concorrente", "Confeitaria Exemplo", 4)], brutos, resumo)
reels, perfis = [], []

# Anúncios: scripts/coleta_anuncios.py + resumo_anuncios.py. Uma ficha por cartão, na mesma ordem:
# [gancho, promessa, oferta, CTA, consciência, etapa do funil, é lançamento?]
cartoes, F = [], []

D = {
 "data": "05/11/2026",
 # Quem é. Os pronomes deixam o texto das abas certo pra homem ou mulher ("ele/dele/do/Do/sozinho/exposto").
 "cli": {"id": "cli", "nome": "Ateliê Doce Ofício", "curto": "Doce Ofício", "quem": "empresa fictícia", "at": "@exemplo.doceoficio", "seg": "não visto", "yt": "não visto",
         "titulo": "Como se apresenta e o registro profissional achado", "hub": "exemplo.invalid", "cnpj": "empresa fictícia · cidade fictícia",
         "ela": "ela", "dela": "dela", "da": "da", "Da": "Da", "sozinha": "sozinha", "exposta": "exposta"},
 # Grupos de concorrente do nicho. A chave vai em conc[].grupo; secular=True / ref=True marcam quem entra só como referência.
 "grupos": {"publico": "vendem pro mesmo público", "formacao": "vendem formação"},
 "gruposTitulo": {"publico": "Vendem pro mesmo público", "formacao": "Formação de profissionais"},
 "txt": {
   "h1": "O mercado da <em>profissão dela</em>, aba por aba.",
   "faixaProdutos": "de R$ X a R$ Y",
   "tile4": ["Rótulo do 4º quadro do resumo", "valor", "explicação curta"],
   "mapa": ["← EIXO ESQUERDO", "EIXO DIREITO →", "canto de cima à direita"],
   "legendaMapa": "Eixo vertical: maior preço publicado (escala log). <b style=\"color:var(--verde)\">Verde</b> é a Doce Ofício.",
   "varremosFora": "quantos nomes foram conferidos e ficaram de fora, e onde está a lista",
   "produtosH2": "N produtos, do mais barato ao mais caro",
   "fontesProdutos": ["site", "checkout"],
   "cliProdutoLinha": ["Doce Ofício", "produto principal", "preço", "garantia", "bônus", "escada"],
   "repH2": "O que falam da Doce Ofício na internet", "repFontes": ["Reclame Aqui", "comentários"], "temasLbl": "Do que criticam nos comentários",
   "ytH2": "Onde ela domina, e quem ensina o tema de graça", "ytFontes": ["YouTube · canal dela"], "ytFora": "",
   "ytLeitura": "Leitura nossa: ...",
   "custoReels": "US$ 0,00",
   "reelsRodape": "Como a coleta foi feita e quem ficou sem coletar.",
   "histDe": "da Doce Ofício",
   "agendaLbl": "Agenda pública", "fontesLanc": ["páginas dos eventos"],
   "fontesPublico": ["comentários"], "fontesFunil": ["linktr.ee"],
 },
 # Confiança geral e por achado: "alta", "moderada" ou "baixa" (o quanto a conclusão aguenta, dado o que foi coletado).
 "confianca": ["moderada", "O que sustenta e o que pesa contra, em uma ou duas frases."],
 "achados": [["Achado 1 em uma frase.", "Explicação com número e fonte.", "alta"]],
 "cliPrecos": [["Doce Ofício · produto", 100]],
 "cliLinha": {"maior": "R$ 100", "gar": "7 dias", "escada": "R$ X → R$ Y", "vende": "Reel → página → checkout"},
 "produtos": [{"nome": "Produto", "grupo": "Formato · público", "preco": 100, "txt": "R$ 100 à vista", "fatos": ["fato"], "por": "Como ela descreve", "fonte": "site"}],
 # Concorrentes. x = posição no eixo do mapa (0 a 1), preco_y = maior preço publicado (None = fora do mapa).
 "conc": [{"id": "confeitaria-exemplo", "nome": "Confeitaria Exemplo", "at": "@confeitaria-exemplo", "grupo": "publico", "origem": "Busca", "seg": "nc", "yt": "não visto", "ytn": 0,
           "motivo": "Por que é concorrente (vende produto parecido pro mesmo público).", "promessa": "—", "preco": None, "precoTxt": "não publicado",
           "produto": "—", "garantia": "—", "bonus": "—", "degrau": "—", "funil": ["Reel", "Página"], "fraco": "Onde é fraca.", "x": .5, "preco_y": None}],
 "cliMapa": {"x": .5, "preco_y": 100},
 "espacos": [["Onde ela está sozinha", "Título", "Explicação"], ["Onde ela está exposta", "Título", "Explicação"]],
 "rep": {"tiles": [["Reclame Aqui", "não visto", "—"]], "canais": [["Canal", "resumo", [0, 100, 0]]], "semDado": [], "temas": [],
         "elogios": [], "queixas": [], "leituras": [], "conc": [], "nicho": []},
 "ytKpi": [["Inscritos", "—"]], "ytCanais": [["Doce Ofício", 1]], "ytTop": [], "ytGratis": [],
 "reelsIG": reels, "perfisIG": perfis, "leiturasReels": [],
 "ads": [],  # anúncios de terceiros que usam o nome dela; vazio esconde a subaba
 "quemAnuncia": [{"nome": "Doce Ofício", "cli": True, "total": 0, "ativos": 0, "venc": 0, "longo": 0, "copys": 0, "formatos": "—", "destinos": "—"}],
 "anunciosConc": cartoes, "fichasAds": fichas(cartoes, F),
 "padroesConc": [], "histAds": [], "histObs": "", "adsColeta": "05/11/2026", "adsSemAnuncio": "",
 "agenda": [], "passado": [], "lancConc": [], "bf": [],
 "busca": [["termo buscado", "primeiros resultados", "posição dela"]], "buscaObs": "", "buscaYt": None,
 "voz": [], "dorCopy": [], "decisao": [], "atrai": [], "repele": [], "objecoes": [],
 "persona": {"texto": "Leitura nossa a partir de ...", "campos": [["Idade", "—"]]},
 "eixos": [["Quem compra", "...", ["a", "b", "c"], "FATO"]],
 "igual": [], "ninguem": [], "naoOlhaTitulo": "Público que ninguém olha", "naoOlha": "",
 "camadas": {"cols": ["Doce Ofício", "Confeitaria Exemplo"], "linhas": [["Critério", ["sim", "nao"]]]},
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

# Dados inventados para o painel abrir cheio, sem coleta nenhuma.
D["selo"] = "Dados fictícios"
D["txt"]["produtosH2"] = "3 produtos, do mais barato ao mais caro"
D["txt"]["cliProdutoLinha"] = ["Doce Ofício", "Formação confeiteira", "R$ 490", "7 dias", "—", "R$ 39 → R$ 197 → R$ 490"]
D["periodo"] = "só para exemplo"
D["cli"].update(titulo="Confeitaria fictícia que vende encomendas e cursos", seg="12 mil seguidores", yt="2 mil inscritos")
D["confianca"] = ["moderada", "Exemplo: a leitura se apoia em preços públicos fictícios, sem acesso aos números internos."]
D["achados"] = [["O nicho concentra os preços abaixo de R$ 200.", "Exemplo: 2 dos 3 produtos ficam nessa faixa, e o curso completo sai por R$ 490.", "alta"],
                ["Ninguém fala de encomenda para empresas.", "Exemplo: nenhum concorrente fictício publica oferta para esse público.", "moderada"],
                ["As reclamações falam mais de prazo do que de preço.", "Exemplo: leitura nossa a partir de comentários inventados.", "baixa"]]
D["produtos"] = [{"nome": "Oficina de bolos", "grupo": "Curso · iniciantes", "preco": 39, "txt": "R$ 39 à vista", "fatos": ["2 horas gravadas"], "por": "Comece a confeitar em casa", "fonte": "site fictício"},
                 {"nome": "Doces para vender", "grupo": "Curso · renda extra", "preco": 197, "txt": "R$ 197 à vista", "fatos": ["12 aulas"], "por": "Do zero à primeira encomenda", "fonte": "site fictício"},
                 {"nome": "Formação confeiteira", "grupo": "Formação · profissionais", "preco": 490, "txt": "R$ 490 à vista", "fatos": ["6 meses de acesso"], "por": "Transforme doce em negócio", "fonte": "site fictício"}]
D["cliPrecos"] = [["Doce Ofício · Oficina", 39], ["Doce Ofício · Doces para vender", 197], ["Doce Ofício · Formação", 490]]
D["cliLinha"] = {"maior": "R$ 490", "gar": "7 dias", "escada": "R$ 39 → R$ 197 → R$ 490", "vende": "Reel → página → checkout"}
D["conc"][0].update(promessa="Doces artesanais em 30 dias", preco=297, precoTxt="R$ 297", produto="Curso de doces", garantia="7 dias", degrau="Curso", seg="8 mil", fraco="Não atende empresas.", preco_y=297, x=.3)
D["txt"]["h1"] = "O mercado do <em>Ateliê Doce Ofício</em>, aba por aba."
D["txt"]["faixaProdutos"] = "de R$ 39 a R$ 490"
D["txt"]["tile4"] = ["Preço mais alto do nicho", "R$ 490", "valor fictício"]
D["txt"]["custoReels"] = "US$ 0,00 (exemplo)"
D["perfisIG"] = [{"h": "exemplo.doceoficio", "nome": "Doce Ofício", "dias": 12, "reels": 18, "de": "2026-09-01", "ate": "2026-10-30", "mediana": 4200, "maior": 31000,
                  "coment_med": 14, "com_palavra": 3, "palavras": ["BOLO"], "com_direct": 2}]
D["reelsIG"] = [{"de": "Doce Ofício", "h": "exemplo.doceoficio", "views": 31000, "data": "2026-10-12", "dur": 32, "likes": 900, "coment": 41, "url": "https://exemplo.invalid/reel",
                 "palavra": "BOLO", "legenda": "Reel fictício do exemplo.", "capa": None}]
D["fontes"] = [["coleta", "Dados fictícios do exemplo", "https://exemplo.invalid", "todas as abas", "05/11/2026"]]
D["limites"] = ["Este painel é só um exemplo: nenhum dado aqui é real."]
