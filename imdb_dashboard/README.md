# Dashboard IMDb de filmes (Power BI)

Análise de ~10 mil filmes do dataset `imdb_movies.csv` (Kaggle), com limpeza em Python e dashboard em Power BI.

## O que o dashboard responde
| Página | Pergunta |
|---|---|
| Avaliação dos filmes | Como se distribuem as notas? Quais gêneros têm a melhor nota média? |
| Filmes bem avaliados | Em que décadas, idiomas e países estão os filmes com nota ≥ 80? |
| Sucesso comercial | Receita e nota andam juntas? Quais são os filmes de maior receita? |
| Orçamento e avaliação | Gastar mais garante nota maior? |

## Estrutura
```
limpeza_imdb.py                     # limpeza dos dados (Python / pandas)
data/raw/imdb_movies.csv            # dados originais (não incluído; coloque aqui para rodar o script)
data/clean/imdb_filmes_limpos_powerbi.csv
imdb_dashboard.pbip                 # projeto do Power BI (abra este arquivo)
imdb_dashboard.Report/              # páginas e visuais
imdb_dashboard.SemanticModel/       # tabelas, relacionamento e medidas DAX
GUIA_DE_APRENDIZADO.md              # explicação de tudo que foi feito
```

## Decisões de limpeza (resumo)
- Nota 0 = filme sem avaliação (vira vazio).
- 179 filmes duplicados (mesmo título e data) removidos.
- Receita/orçamento com casas decimais são valores imputados pelo dataset e ficam fora das análises (`receita_suspeita`, `orcamento_suspeito`).
- País "AU" é um valor padrão do dataset e aparece como "Indefinido" em `pais_analise`.
- Gêneros separados em tabela própria para cada filme contar em todos os seus gêneros.

## Fonte dos dados
Dataset público "IMDB Movies Dataset" (Kaggle). Créditos aos autores originais.
