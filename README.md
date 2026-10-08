# 🎬 Análise de filmes IMDb: avaliação do público e desempenho financeiro

Projeto de análise de dados com **Python e Power BI** para explorar a relação entre avaliação do público, orçamento e receita de filmes. A investigação combina preparação dos dados, análise exploratória e comunicação dos resultados em um dashboard.

## Contexto de negócio

Uma empresa de produção e distribuição de filmes deseja entender onde investir: quais características estão associadas a boas avaliações e quais estão relacionadas ao desempenho financeiro?

A pergunta central é: **filmes bem avaliados também são os que mais faturam?** O objetivo é investigar essa relação com evidências, reconhecer as limitações da base e identificar informações necessárias para apoiar decisões de investimento.

## Perguntas de negócio

O enunciado apresenta oito perguntas e uma questão complementar sobre orçamento:

| Bloco | Pergunta |
| --- | --- |
| Entendendo o cenário | Além do gênero, o que parece influenciar a nota de um filme? |
| Entendendo o cenário | Quais informações estão ausentes e como poderiam ser obtidas? |
| Aceitação do público | Filmes muito bem avaliados têm características em comum além do gênero e do orçamento? |
| Aceitação do público | As informações sobre quem trabalhou nos filmes são suficientes para explicar seu destaque? |
| Aceitação do público | Como investigar padrões de sucesso ligados a diretores, produtores e roteiristas? |
| Retorno financeiro × aceitação | Os filmes de maior receita são também os mais bem avaliados? |
| Retorno financeiro × aceitação | O que pode explicar receita alta com nota mediana ou baixa? |
| Retorno financeiro × aceitação | Filmes da mesma franquia se comportam de forma semelhante em nota e receita? |
| Questão complementar | Qual é a relação entre orçamento e avaliação do público? |

## Ferramentas utilizadas

- **Python:** preparação e transformação dos dados.
- **pandas e NumPy:** tratamento de valores ausentes, duplicidades e criação de indicadores.
- **Power BI:** exploração visual e apresentação das análises.
- **PBIP:** formato do projeto do Power BI.

## Fonte dos dados

A base utilizada é `imdb_movies.csv`, identificada na documentação original como proveniente do dataset público **IMDB Movies Dataset**, no Kaggle. Ela reúne título, lançamento, gênero, nota, idioma, país, elenco, orçamento e receita.

O endereço exato da publicação e sua licença precisam ser confirmados antes de redistribuir os dados. Os créditos da base pertencem aos seus respectivos autores.

## Preparação dos dados

O script `limpeza_imdb.py` realiza:

1. Padronização de textos, espaços e valores ausentes.
2. Conversão de notas, orçamento e receita para valores numéricos.
3. Tratamento de notas menores ou iguais a zero como ausentes.
4. Conversão de datas e criação das colunas de ano e década.
5. Remoção de filmes sem título e duplicados por título e data de lançamento.
6. Identificação de conflitos financeiros entre registros duplicados.
7. Criação de campos financeiros destinados à análise.
8. Criação de faixas de nota e orçamento e classificação dos filmes bem avaliados.
9. Extração de atores do campo `crew`, considerando sua estrutura de atores e personagens.
10. Exportação dos dados tratados em CSV com codificação `utf-8-sig`.

### Critérios de qualidade dos dados financeiros

| Indicador | Regra implementada |
| --- | --- |
| `receita_suspeita` | Receita positiva repetida em três ou mais registros; mesmo título e receita em dois ou mais registros; casas decimais; valor inferior a 1.000; ou receita informada para status diferente de `Released`. |
| `orcamento_suspeito` | Orçamento inferior a 1.000 ou com casas decimais. |
| `orcamento_revisar` | Orçamento de 1.000 até menos de 100.000; permanece na análise quando não há outro impedimento. |
| `financeiro_conflitante` | Orçamento ou receita divergentes entre registros com o mesmo título e data. |

Essas regras são **heurísticas de triagem**, não comprovação de erro ou imputação. Repetições e casas decimais precisam ser verificadas na fonte. As exclusões também podem alterar a amostra e influenciar os resultados.

Os valores de orçamento e receita são preservados em campos próprios. Para as análises financeiras, o script disponibiliza `orcamento_analise` e `receita_analise`, que excluem registros sinalizados conforme as regras acima.

O código substitui `AU` por `Indefinido` em `pais_analise`, mantendo o valor original em `pais`. Essa decisão exige validação na documentação da base: o código sozinho não comprova que os registros australianos estejam incorretos.

### Indicadores derivados

- **Bem avaliado:** filme com `score ≥ 80`, na escala utilizada pela base.
- **Financeiro confiável:** registros com orçamento e receita disponíveis após a triagem; o nome do indicador não representa auditoria externa dos valores.
- **`lucro`:** receita menos orçamento quando ambos passam pela triagem. É uma diferença simplificada, sem considerar marketing, distribuição e participação dos exibidores.
- **`roi`:** o script calcula `receita ÷ orçamento`, um múltiplo de receita sobre orçamento. Esse indicador difere do ROI percentual convencional, calculado como `(receita − orçamento) ÷ orçamento`.

## Dashboard

Conforme a documentação original, o dashboard está organizado em quatro páginas:

| Página | Foco |
| --- | --- |
| Avaliação dos filmes | Distribuição das notas e comparação entre gêneros. |
| Filmes bem avaliados | Filmes com score ≥ 80 por década, idioma e país. |
| Sucesso comercial | Relação entre receita e nota e filmes de maior receita. |
| Orçamento e avaliação | Relação entre investimento e avaliação e qualidade dos dados financeiros. |

As perguntas sobre profissionais de produção e franquias exigem investigação complementar; essas páginas não resolvem, por si só, todas as questões do enunciado.

## Principais observações

As respostas registradas em `1-Perguntas-de-negocio.docx` apontam que:

- **Receita alta não garante nota alta.** O documento menciona grandes sucessos comerciais com avaliações diferentes, como *Avengers: Endgame*, *Avatar* e *Jurassic World*.
- **Os filmes bem avaliados apresentam diferenças por período, idioma e país.** A maior presença nas décadas de 2010 e 2020 precisa ser contextualizada pelo total de filmes disponível em cada período.
- **Maior orçamento não garante melhor avaliação.** A interpretação registrada não sustenta uma relação automática entre investimento e nota.
- **O campo `crew` não atende à análise dos profissionais de produção.** Ele contém principalmente atores e personagens, faltando informações específicas sobre direção, roteiro e produção.
- **Reconhecimento de franquias é uma possível explicação para receita alta com avaliação moderada.** Essa hipótese exige dados adicionais para ser testada.

Essas observações resumem o documento de respostas. Os resultados não foram recalculados para este README, pois o dataset e as pastas completas do dashboard não estão entre os arquivos fornecidos. As relações exploradas são descritivas e não demonstram causalidade.

## Limitações e próximos passos

- Obter comentários dos espectadores e quantidade de votos para contextualizar as avaliações.
- Complementar a base com diretores, roteiristas e produtores, usando identificadores dos filmes para evitar confusão entre títulos homônimos.
- Identificar franquias e a ordem das sequências para comparar seus resultados.
- Validar países e valores financeiros na fonte e comparar análises com e sem as regras de exclusão.
- Considerar inflação, período de lançamento, distribuição e marketing nas comparações financeiras.
- Comparar médias junto com o tamanho dos grupos e a proporção de filmes bem avaliados.

## Estrutura do projeto

Estrutura esperada para executar a limpeza e abrir o projeto completo:

```text
.
├── README.md
├── limpeza_imdb.py
├── 1-Perguntas-de-negocio.docx
├── imdb_dashboard.pbip
├── imdb_dashboard.Report/
├── imdb_dashboard.SemanticModel/
└── data/
    ├── raw/
    │   └── imdb_movies.csv
    └── clean/
        └── imdb_filmes_limpos_powerbi.csv
```

O CSV original, o CSV tratado e as pastas `.Report` e `.SemanticModel` não estão entre os arquivos fornecidos nesta versão. O `.pbip` referencia `imdb_dashboard.Report`; ele não contém sozinho todos os visuais e dados do relatório.

## Como executar

### 1. Preparar o ambiente

Com Python instalado, execute na pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente no Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Ou no Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install pandas numpy
```

### 2. Executar a limpeza

Coloque o arquivo original em `data/raw/imdb_movies.csv` e execute:

```bash
python limpeza_imdb.py
```

O script cria a pasta de saída e gera `data/clean/imdb_filmes_limpos_powerbi.csv`. Durante a execução, informa a quantidade de linhas, duplicados removidos e registros sinalizados.

### 3. Abrir o dashboard

Com as pastas completas do relatório e do modelo disponíveis, abra `imdb_dashboard.pbip` no Power BI Desktop com suporte ao formato PBIP. Ajuste o caminho da fonte de dados para o CSV tratado e atualize o relatório.

## Aprendizados

O projeto exercita a tradução de perguntas de negócio em análises, a preparação de dados com Python e a comunicação de resultados no Power BI. Um aprendizado central é reconhecer o que a base permite responder e quais informações ainda precisam ser obtidas antes de recomendar investimentos.
