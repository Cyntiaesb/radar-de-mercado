# Radar de Mercado

Descobre quanto os concorrentes cobram, como se posicionam, o que falam deles, o que anunciam e o que publicam. Tudo vira um painel em HTML, com uma aba para cada análise.

O painel de exemplo está em [`painel/exemplo.html`](painel/exemplo.html). Abra no navegador. **A empresa e todos os dados desse exemplo são fictícios.**

## O que cada parte faz

| Etapa | Script | Usa | Custo |
|---|---|---|---|
| Reels dos perfis | `coleta_reels.py` + `resumo_reels.py` | Apify | US$ por rodada, com teto |
| Anúncios da Biblioteca da Meta | `coleta_anuncios.py` + `anunciantes.py` + `resumo_anuncios.py` | Apify | US$ por rodada, com teto |
| Reputação no Reclame Aqui e no Reddit | `coleta_reputacao.py` | Apify | cerca de US$ 0,01 por reclamação |
| Comentários do YouTube | `coleta_reputacao.py` | yt-dlp | sem custo |
| Nomes de marca: INPI, domínios e busca | `analise_nomes.py` | serviços públicos | sem custo |
| Painel | `monta_painel.py` | Python | sem custo |
| PDF do painel | `painel_pdf.py` | Edge ou Chrome | sem custo |

**Preços dos produtos e leitura do posicionamento não são coletados sozinhos.** Os scripts juntam o material. Quem pesquisa os preços nas páginas e escreve a leitura é você, com a ajuda do Claude Code, no arquivo da empresa estudada.

## Como instalar

Precisa de Python 3.10 ou mais novo. O Node.js é opcional: ele confere se o painel abre sem erro.

```bash
git clone https://github.com/Cyntiaesb/radar-de-mercado.git
cd radar-de-mercado
pip install -r requirements.txt
python tests/teste_local.py
```

Para as coletas pelo Apify, crie uma conta em [apify.com](https://apify.com), copie `.env.example` para `.env` e cole o seu token. Nunca publique esse arquivo.

## Como usar

Troque `meu-estudo` pelo nome do estudo, em minúsculas e sem espaço.

**1. Colete os reels e os anúncios**

```bash
python scripts/coleta_reels.py meu-estudo @perfil @concorrente --desde 2026-01-01 --teto 2
python scripts/resumo_reels.py meu-estudo @perfil @concorrente
python scripts/coleta_anuncios.py meu-estudo "site-do-concorrente.com.br" --teto 2
python scripts/anunciantes.py meu-estudo
python scripts/resumo_anuncios.py meu-estudo "Nome exato da página"
```

**2. Colete reputação e nomes, se quiser**

```bash
python scripts/coleta_reputacao.py meu-estudo --reclameaqui slug-da-empresa --youtube id-do-video --teto 1
python scripts/analise_nomes.py meu-estudo "Nome da Marca" --setor "seu setor"
```

**3. Escreva o estudo**

Copie `especialistas/_novo.py` para `especialistas/meu-estudo.py` e preencha. O esqueleto explica cada campo. Ali entram concorrentes, preços, posicionamento e leitura. Dá para pedir ao Claude Code que preencha a partir da pasta `coletas/meu-estudo/`.

**4. Monte o painel**

```bash
python scripts/monta_painel.py meu-estudo
python scripts/painel_pdf.py meu-estudo
```

O painel fica em `painel/meu-estudo.html`. Se faltar alguma informação, o script avisa qual é.

## Regras do painel

- Número de coleta sai de script, nunca digitado de cabeça.
- O que não foi visto entra como "não visto".
- "Leitura nossa" é interpretação. O resto é fato com fonte.
- Cada conclusão leva um selo de confiança: alta, moderada ou baixa.

## Limites

- O preenchimento do estudo é manual: os scripts não preenchem o painel sozinhos.
- Os coletores dependem de terceiros e podem parar quando esses serviços mudarem.
- O custo do Apify varia. Use sempre o `--teto`, que limita o gasto de cada rodada.
- Reddit e Reclame Aqui por nome podem trazer homônimos. Confira antes de usar.
- A aba de nomes mostra presença pública. Não é parecer de disponibilidade: para registrar uma marca, procure um advogado.
- Coletas ficam só na sua máquina, em `coletas/`, fora do Git. Colete dados públicos e respeite a LGPD e os termos de cada plataforma.

## Licença

MIT. Veja [LICENSE](LICENSE).
