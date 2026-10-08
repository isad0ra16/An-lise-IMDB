"""
Limpeza do dataset IMDB (imdb_movies.csv) para análise no Power BI.

Estrutura esperada do repositório:
    limpeza_imdb.py
    data/raw/imdb_movies.csv                      <- arquivo original (entrada)
    data/clean/imdb_filmes_limpos_powerbi.csv     <- arquivo limpo (saída)
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd

# 1. CAMINHOS DOS ARQUIVOS (relativos à pasta do script, funciona em qualquer máquina)
BASE = Path(__file__).resolve().parent
entrada = BASE / "data" / "raw" / "imdb_movies.csv"
saida = BASE / "data" / "clean" / "imdb_filmes_limpos_powerbi.csv"
saida.parent.mkdir(parents=True, exist_ok=True)

# 2. LER O CSV ORIGINAL
df = pd.read_csv(entrada)

print("Dataset carregado!")
print("Linhas:", len(df))
print("Colunas:", len(df.columns))

# 3. LIMPAR COLUNAS DE TEXTO
# Além de tirar espaços das pontas, troca o espaço "invisível" (\xa0) por espaço normal.
# Sem isso, "Drama,\xa0Action" não separa direito por vírgula.
colunas_texto = ["genre", "orig_title", "overview", "names", "crew",
                 "status", "orig_lang", "country"]

for coluna in colunas_texto:
    df[coluna] = (
        df[coluna].astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df[coluna] = df[coluna].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

# 4. TRANSFORMAR NOTA, ORÇAMENTO E RECEITA EM NÚMEROS
df["score"] = pd.to_numeric(df["score"], errors="coerce")
df["budget_x"] = pd.to_numeric(df["budget_x"], errors="coerce")
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

# Nota 0 não é nota: é filme sem avaliação (ou ainda não lançado). Vira ausente.
df["score"] = df["score"].where(df["score"] > 0, np.nan)

# 5. CORRIGIR A DATA
df["data_lancamento"] = pd.to_datetime(
    df["date_x"].astype(str).str.strip(),
    format="%m/%d/%Y",
    errors="coerce"
)
df["ano"] = df["data_lancamento"].dt.year
df["decada"] = (df["ano"] // 10) * 10

# 6. CRIAR NOMES MAIS FÁCEIS PARA O POWER BI
# titulo = nome em inglês (names); o título no idioma original fica em outra coluna
df["titulo"] = df["names"].fillna(df["orig_title"])
df["titulo_original"] = df["orig_title"]
df["genero"] = df["genre"]
df["idioma_original"] = df["orig_lang"]
df["pais"] = df["country"]
df["sinopse"] = df["overview"]
df["elenco_personagens"] = df["crew"]   # na verdade é "ator, personagem, ator, personagem..."

# Remover filmes sem título
df = df[df["titulo"].notna()].copy()

# 7. TRATAR FILMES DUPLICADOS (mesmo título + mesma data)
# Os duplicados têm orçamento/receita diferentes: são filmes homônimos que herdaram
# valores um do outro. Mantemos uma linha por filme e, quando os valores financeiros
# são conflitantes, não dá para saber qual é o certo, então marcamos como conflito.
chave = ["titulo", "data_lancamento"]
n_antes = len(df)

grupo = df.groupby(chave, dropna=False)
conflito = (
    (grupo["budget_x"].transform(lambda s: s.nunique(dropna=False)) > 1)
    | (grupo["revenue"].transform(lambda s: s.nunique(dropna=False)) > 1)
)
df["financeiro_conflitante"] = np.where(conflito, "Sim", "Não")

df = df.drop_duplicates(subset=chave, keep="first").copy()
print("Duplicados removidos:", n_antes - len(df))

# 8. PREPARAR RECEITA
df["receita"] = df["revenue"].where(df["revenue"] > 0, np.nan)

# Receita "placeholder": o mesmo valor exato repetido em 3+ filmes diferentes
# (ex.: 175269998.8 aparece em 143 filmes) é preenchimento do dataset, não receita real.
repeticoes = df.groupby("receita")["receita"].transform("size")
receita_repetida = df["receita"].notna() & (repeticoes >= 3)

# Homônimos que herdaram a receita um do outro: mesmo título e mesma receita em 2+ filmes
# (ex.: "Titanic" de 1953 com a receita do "Titanic" de 1997). Não dá para saber qual é o
# verdadeiro, então marcamos todos como suspeitos.
receita_homonimo = df["receita"].notna() & (
    df.groupby(["titulo", "receita"])["receita"].transform("size") >= 2
)

# Receita com casas decimais (ex.: 175269998.8) é valor imputado/estimado pelo dataset:
# receitas reais são números inteiros. As decimais têm mediana ~8x maior que as inteiras
# e dão resultados absurdos (ex.: "Rathinirvedam", 1978, com US$ 1,9 bilhão).
receita_imputada = df["receita"].notna() & ((df["receita"] % 1) != 0)

# Receita muito baixa (< 1.000) ou de filme ainda não lançado também não é confiável
receita_baixa = df["receita"].notna() & (df["receita"] < 1000)
nao_lancado = df["status"] != "Released"

df["receita_suspeita"] = np.where(
    receita_repetida | receita_homonimo | receita_imputada | receita_baixa | (nao_lancado & df["receita"].notna()),
    "Sim", "Não"
)

# Receita usada nas análises
df["receita_analise"] = df["receita"].where(
    (df["receita_suspeita"] == "Não") & (df["financeiro_conflitante"] == "Não"),
    np.nan
)

# 9. PREPARAR ORÇAMENTO
df["orcamento"] = df["budget_x"]

# Suspeito = menor que 1.000 (erro de digitação/unidade) OU com casas decimais
# (valor imputado pelo dataset, mesma lógica da receita)
df["orcamento_suspeito"] = np.where(
    df["orcamento"].notna() & ((df["orcamento"] < 1000) | ((df["orcamento"] % 1) != 0)),
    "Sim", "Não"
)

# Entre 1.000 e 100.000: pode ser real (filme independente) ou erro. Fica nas análises,
# mas marcado para você decidir no Power BI.
df["orcamento_revisar"] = np.where(
    df["orcamento"].notna() & (df["orcamento"] >= 1000) & (df["orcamento"] < 100_000),
    "Sim", "Não"
)

# Orçamento usado nas análises
df["orcamento_analise"] = df["orcamento"].where(
    (df["orcamento_suspeito"] == "Não") & (df["financeiro_conflitante"] == "Não"),
    np.nan
)

# 10. FINANCEIRO CONFIÁVEL, LUCRO E ROI (só quando orçamento E receita são confiáveis)
df["financeiro_confiavel"] = np.where(
    df["orcamento_analise"].notna() & df["receita_analise"].notna(),
    "Sim", "Não"
)
confiavel = df["financeiro_confiavel"] == "Sim"
df["lucro"] = (df["receita_analise"] - df["orcamento_analise"]).where(confiavel)
df["roi"] = (df["receita_analise"] / df["orcamento_analise"]).where(confiavel)

# 11. CRIAR FAIXAS DE ORÇAMENTO
faixas_orcamento = [-np.inf, 10_000_000, 50_000_000, 100_000_000, 200_000_000, np.inf]
nomes_faixas = ["Até 10 milhões", "10 a 50 milhões", "50 a 100 milhões",
                "100 a 200 milhões", "Acima de 200 milhões"]

df["faixa_orcamento"] = pd.cut(
    df["orcamento_analise"], bins=faixas_orcamento, labels=nomes_faixas, right=False
).astype("string")
df["faixa_orcamento"] = df["faixa_orcamento"].fillna("Sem orçamento válido")

# 12. CRIAR FAIXAS DE NOTA
faixas_score = [-np.inf, 50, 60, 70, 80, np.inf]
nomes_score = ["Abaixo de 50", "50 a 59", "60 a 69", "70 a 79", "80 ou mais"]

df["faixa_score"] = pd.cut(
    df["score"], bins=faixas_score, labels=nomes_score, right=False
).astype("string")
df["faixa_score"] = df["faixa_score"].fillna("Sem nota")

# 13. CLASSIFICAR OS FILMES
df["classificacao_score"] = np.select(
    [df["score"].isna(), df["score"] >= 80],
    ["Sem nota", "Bem avaliado"],
    default="Abaixo de 80"
)

# 14. GÊNEROS E ELENCO
df["genero_principal"] = df["genero"].str.split(", ").str[0]
df["qtd_generos"] = df["genero"].str.split(", ").str.len()


def extrair_atores(texto):
    """A coluna crew vem como 'ator, personagem, ator, personagem...'.
    Pega os atores (posições pares). Junta 'Jr.', 'Sr.' ao nome anterior.
    Se a lista não ficar par, não dá para ter certeza e devolve vazio."""
    if pd.isna(texto):
        return pd.NA
    partes = []
    for item in texto.rstrip(", ").split(", "):
        if partes and re.fullmatch(r"(Jr\.?|Sr\.?|II|III)", item):
            partes[-1] = partes[-1] + ", " + item
        else:
            partes.append(item)
    if len(partes) % 2 != 0:
        return pd.NA
    return " | ".join(partes[0::2])


df["atores"] = df["elenco_personagens"].apply(extrair_atores)
df["qtd_atores"] = df["atores"].str.split(" | ", regex=False).str.len()

# 15. PAÍS
# "AU" aparece em quase metade dos filmes (inclusive filmes japoneses e americanos):
# é um valor padrão do dataset, não o país real. Mantemos o original em "pais"
# e criamos "pais_analise" sem esse valor.
df["pais_analise"] = df["pais"].where(df["pais"] != "AU", "Indefinido")

# 16. CRIAR INDICADORES DE DADOS DISPONÍVEIS
df["possui_orcamento"] = df["orcamento_analise"].notna().astype(int)
df["possui_receita"] = df["receita_analise"].notna().astype(int)
df["possui_genero"] = df["genero"].notna().astype(int)
df["possui_elenco"] = df["elenco_personagens"].notna().astype(int)
df["possui_nota"] = df["score"].notna().astype(int)

# 17. SELECIONAR AS COLUNAS FINAIS
df = df.sort_values(["data_lancamento", "titulo"], ascending=[False, True]).reset_index(drop=True)
df.insert(0, "id", df.index + 1)

colunas_finais = [
    "id", "titulo", "titulo_original", "data_lancamento", "ano", "decada",
    "score", "faixa_score", "classificacao_score",
    "genero", "genero_principal", "qtd_generos",
    "sinopse", "elenco_personagens", "atores", "qtd_atores",
    "status", "idioma_original", "pais", "pais_analise",
    "orcamento", "orcamento_suspeito", "orcamento_revisar", "orcamento_analise", "faixa_orcamento",
    "receita", "receita_suspeita", "receita_analise",
    "financeiro_conflitante", "financeiro_confiavel", "lucro", "roi",
    "possui_orcamento", "possui_receita", "possui_genero", "possui_elenco", "possui_nota",
]
limpo = df[colunas_finais].copy()

# 18. SALVAR O DATASET LIMPO
limpo.to_csv(saida, index=False, encoding="utf-8-sig")

print("\nArquivo salvo em:", saida)
print("Linhas finais:", len(limpo))
print("Sem nota:", int((limpo["classificacao_score"] == "Sem nota").sum()))
print("Receita suspeita:", int((limpo["receita_suspeita"] == "Sim").sum()))
print("Financeiro conflitante:", int((limpo["financeiro_conflitante"] == "Sim").sum()))
print("Financeiro confiável:", int((limpo["financeiro_confiavel"] == "Sim").sum()))
