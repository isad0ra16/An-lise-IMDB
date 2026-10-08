# Guia de aprendizado: como o dashboard foi refeito

Este guia explica **o que foi feito, por que, e como você faria sozinha**.

> **Aviso honesto:** o projeto foi gerado sem o Power BI Desktop à mão, então pode aparecer algum erro ao abrir (já apareceu um: ver seção 2.4). Se acontecer, copie a mensagem e peça a correção.

---

## 1. Como abrir

1. Descompacte a pasta em um lugar fixo, por exemplo `C:\imdb_dashboard`.
2. No Power BI Desktop, **Arquivo → Abrir** e escolha `imdb_dashboard.pbip`.
3. Vá em **Transformar dados → Gerenciar parâmetros → CaminhoCSV** e coloque o caminho completo do arquivo `data\clean\imdb_filmes_limpos_powerbi.csv` na sua máquina. Clique em **Fechar e Aplicar**.
4. Para virar um `.pbix` único: **Arquivo → Salvar como → .pbix**.
5. Para o GitHub: **Arquivo → Exportar → PDF** e salve o PDF e prints das 4 páginas em `docs/`.

**Filtros sincronizados:** cada página tem 3 filtros no topo (Década, Gênero, Idioma). Para que a escolha valha nas 4 páginas: **Exibir → Sincronizar segmentações**.

---

## 2. O que mudou na arquitetura (e por quê)

### 2.1 Uma tabela virou duas: `filmes` e `generos`
Antes, a coluna `genero` guardava listas como "Drama, Action". Um gráfico por essa coluna cria **uma barra por combinação**, não por gênero. A solução padrão é uma tabela auxiliar com **uma linha por filme e gênero**. Ela é feita no **Power Query**: `Text.Split` quebra o texto em lista e `Table.ExpandListColumn` transforma cada item em uma linha. As duas tabelas se ligam pelo `id` (relacionamento **muitos para um**), com filtro nos **dois sentidos** para que escolher um gênero também filtre os filmes.

Resultado: **19 gêneros reais**, e cada filme conta em todos os seus gêneros.

### 2.2 `fonte_csv`: ler o arquivo uma vez só
`fonte_csv` lê o CSV e é reaproveitada por `filmes` e `generos`. Se o arquivo mudar de lugar, você altera **um** parâmetro (`CaminhoCSV`).

### 2.3 Colunas que não uso foram removidas
`filmes` não carrega `sinopse`, `elenco` nem `atores`. Menos colunas = arquivo menor e atualização mais rápida.

### 2.4 Coluna calculada e colunas de ordem
| Coluna | Onde é criada | Para quê |
|---|---|---|
| `titulo_ano` | DAX (coluna calculada) | "Titanic (1997)": evita que filmes com o mesmo título se misturem |
| `ordem_faixa_score` | Power Query (M) | Número de 1 a 6 para ordenar as faixas de nota |
| `ordem_faixa_orcamento` | Power Query (M) | Idem para as faixas de orçamento |

**Classificar por coluna:** textos ordenam alfabeticamente, então "Acima de 200 milhões" viria antes de "Até 10 milhões". Em `faixa_score` e `faixa_orcamento` configurei `sortByColumn` apontando para a coluna de ordem. No Power BI: selecionar a coluna → **Ferramentas de coluna → Classificar por coluna**.

**Um erro que aconteceu e vale aprender:** na primeira versão eu criei as colunas de ordem em DAX, a partir da própria faixa (`SWITCH(filmes[faixa_orcamento], ...)`). O Power BI recusou com *"dependência circular"*: a faixa é ordenada pela coluna de ordem, e a coluna de ordem depende da faixa. Regra prática: **uma coluna usada em "Classificar por coluna" não pode ser calculada em DAX a partir da coluna que ela ordena**. A saída é criá-la no Power Query (`Table.AddColumn`), que roda antes do modelo existir e por isso não cria o ciclo.

---

## 3. Medidas DAX: o coração do dashboard

Uma **coluna** calcula uma vez por linha e fica gravada. Uma **medida** calcula na hora, **de acordo com o filtro do momento** (gráfico, segmentação, categoria). Por isso a mesma medida muda de valor em cada barra.

| Medida | Fórmula resumida | Explicação |
|---|---|---|
| Total de filmes | `COUNTROWS(filmes)` | Conta linhas visíveis |
| Filmes com nota | `CALCULATE(COUNTROWS(...), classificacao <> "Sem nota")` | `CALCULATE` conta com um filtro extra |
| Nota média | `AVERAGE(filmes[score])` | Ignora vazios (por isso nota 0 virar vazio importa) |
| Filmes bem avaliados | `CALCULATE(COUNTROWS(...), classificacao = "Bem avaliado")` | Nota ≥ 80 |
| Taxa bem avaliados | `DIVIDE(bem avaliados, com nota)` | `DIVIDE` evita erro de divisão por zero |
| Taxa por idioma / país | `IF(total >= 100, taxa)` | **Truque do vazio:** sem `ELSE`, o `IF` devolve vazio e o gráfico **esconde a categoria**. Assim ficam de fora idiomas/países com amostra pequena |
| Receita total / Orçamento total | `SUM(receita_analise)` | Usa só valores confiáveis |
| ROI mediano | `MEDIAN(filmes[roi])` | Mediana porque a média é distorcida por outliers |
| Orçamentos suspeitos | `CALCULATE(COUNTROWS(...), suspeito = "Sim")` | Conta os marcados |
| Insight ... | `FORMAT(...) & " texto " & ...` | Frase dinâmica: muda com os filtros |

**Por que percentual e amostra mínima?** Com 1 filme bem avaliado em 1 filme, o país teria "100%". Por isso: idiomas com **100+ filmes** e países com **30+ filmes**. O "AU" (valor padrão do dataset) é excluído com `SELECTEDVALUE(...) <> "Indefinido"`.

**Formato `#,0,,`:** as duas vírgulas no final dividem o número por 1 milhão **só na exibição**. Por isso os eixos de receita e orçamento mostram milhões.

---

## 4. Gráfico a gráfico: o que mudou

**Página 1: Avaliação dos filmes**
- 3 cartões (total, nota média, filmes com nota ≥ 80), agora medidas.
- Nota média por gênero: usa `generos[genero]`; antes eram combinações e o filtro "10 mais" ordenava por título.
- Faixas de nota: colunas **em ordem natural**, incluindo "Sem nota".

**Página 2: Filmes bem avaliados**
- Por década: colunas em ordem cronológica.
- Por idioma e por país: trocados de contagem para **% de bem avaliados**, com amostra mínima (o inglês domina qualquer contagem).

**Página 3: Sucesso comercial**
- Dispersão receita × nota: categoria `titulo_ano` e receita confiável.
- Funil virou **barras horizontais** com Top 10 por receita (funil serve para etapas de um processo, não para ranking).

**Página 4: Orçamento e avaliação**
- Cartão de suspeitos simplificado.
- Área empilhada virou **colunas** em ordem de orçamento.
- Dispersão: o eixo X agora é **orçamento** (antes o título dizia "Orçamento", mas o campo era receita).

**Filtros:** Década, Gênero e Idioma em lista suspensa, no topo, fora dos painéis do fundo.

---

## 5. Os fundos
Mantive suas 4 imagens e as posições dentro dos painéis. Como os painéis fazem parte da imagem, se você mover um gráfico ele pode sair do quadro.

---

## 6. Confira se os números batem

| Item | Esperado |
|---|---|
| Total de filmes | 9,999 |
| Filmes com nota | 9,790 |
| Nota média do público | 64,8 |
| Filmes com nota ≥ 80 | 429 (taxa 4,4%) |
| Gêneros distintos | 19 (maior nota: Music 70,0; menor: Horror 60,2) |
| Faixas de nota | 60 a 69: 4.108 · 70 a 79: 2.805 · 50 a 59: 1.858 · Abaixo de 50: 590 · 80 ou mais: 429 · Sem nota: 209 |
| Bem avaliados por década | 1900: 1 · 1920: 3 · 1930: 3 · 1940: 8 · 1950: 18 · 1960: 11 · 1970: 20 · 1980: 25 · 1990: 39 · 2000: 57 · 2010: 125 · 2020: 119 |
| Filmes com financeiro confiável | 5,369 |
| ROI mediano | 2,4x |
| Orçamentos suspeitos | 350 |
| Nota média, orçamento alto (100 mi+) × baixo (até 10 mi) | 63,9 × 65,7 |
| Maior receita | Avatar (2009), cerca de US$ 2.924 milhões |

**% bem avaliados por idioma (100+ filmes):**

| Idioma | Taxa |
|---|---|
| Japanese | 11,6% |
| Spanish, Castilian | 7,7% |
| Korean | 7,5% |
| Italian | 6,6% |
| Chinese | 4,8% |
| French | 4,7% |
| English | 3,2% |
| Cantonese | 2,1% |

**% bem avaliados por país (30+ filmes, sem "AU"):**

| País | Taxa |
|---|---|
| MX | 15,2% |
| IN | 14,8% |
| AR | 12,2% |
| JP | 7,7% |
| KR | 6,6% |
| RU | 6,5% |
| CA | 4,6% |
| GB | 3,6% |
| CN | 3,4% |
| BR | 2,9% |
| PH | 2,9% |
| FR | 2,3% |
| DE | 2,3% |
| US | 2,1% |
| IT | 1,7% |
| ES | 1,3% |
| HK | 0,8% |

---

## 7. Limitações para citar no README do GitHub
- **Financeiro:** receita e orçamento imputados (casas decimais, repetidos entre filmes ou herdados de homônimos) ficam de fora; o dashboard usa 5,369 de 9,999 filmes.
- **ROI** ainda tem outliers; por isso o dashboard usa a **mediana**.
- **País:** quase metade do dataset vem como "AU" (padrão do dataset).
- **Nota:** escala de 0 a 100 (usuários do IMDb).

---

## 8. Treino
Crie do zero um gráfico de colunas de **"Nota média por década"**: `filmes[decada]` no eixo X e a medida **Nota média** em Y, ordenado por década. Se funcionar, você entendeu a relação entre coluna (categoria) e medida (valor).
