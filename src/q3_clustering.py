"""Q3: agrupamento de mercados por perfil de preço.

Decisão 4: dados POR MERCADO, só mercados com série quase completa
(`config.MIN_MESES_MERCADO`). Cada mercado é representado pelo seu preço
relativo em cada produto. Algoritmo: K-Means (aula 11), com k escolhido por
cotovelo, silhueta e índice Xie-Beni (aulas 11 e 12).

Decisão 11 (detalhes em docs/agrupamento_q3.md):
- Pão Francês fica fora (`config.PRODUTOS_Q3`);
- o preço relativo NÃO é padronizado antes do K-Means: todas as colunas já
  estão na mesma unidade (proporção da mediana), então a distância entre
  mercados é diferença de preço de verdade;
- a economia em R$ usa a cesta do DIEESE (`config.CESTA_DIEESE`).

Convenção dos grupos: os rótulos são renumerados por `ordenar_grupos` para que
o grupo 0 seja o MAIS BARATO (menor preço relativo médio). Isso torna os
rótulos comparáveis entre execuções e entre períodos.
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from src import config

# Inicializações do K-Means: com só 25 mercados é barato, e várias
# inicializações evitam um mínimo local ruim.
N_INICIALIZACOES = 20


def _faixa_k(ks) -> range:
    if ks is None:
        return range(config.K_CLUSTERS_MIN, config.K_CLUSTERS_MAX + 1)
    return ks


def montar_matriz_mercados(
    relativo: pd.DataFrame,
    produtos: list[str] | None = None,
    inicio: str | None = None,
    fim: str | None = None,
) -> pd.DataFrame:
    """Monta a matriz de entrada do K-Means: uma linha por mercado, uma coluna
    por produto.

    Cada célula é a MEDIANA do preço relativo do mercado naquele produto, nos
    meses entre `inicio` e `fim` (inclusive; formato "AAAA-MM"; padrão: todo o
    período). A mediana resume o "preço típico" do mercado sem ser puxada por
    um mês de promoção ou de erro.

    Decisão 11: nada é imputado. Se algum mercado não tiver um dos `produtos`
    no período, lança ValueError com as células vazias, para a escolha (tirar
    o produto, o mercado ou preencher) ser feita e justificada fora daqui.

    Args:
        relativo: saída de `aggregation.preco_relativo`.
        produtos: colunas da matriz (padrão: `config.PRODUTOS_Q3`).
        inicio, fim: limites do período, opcionais.
    """
    produtos = config.PRODUTOS_Q3 if produtos is None else produtos
    dados = relativo[relativo["produto"].isin(produtos)]
    if inicio is not None:
        dados = dados[dados["mes"] >= pd.Period(inicio, freq="M")]
    if fim is not None:
        dados = dados[dados["mes"] <= pd.Period(fim, freq="M")]

    matriz = (
        dados.pivot_table(index="mercado", columns="produto", values="relativo", aggfunc="median")
        .reindex(columns=produtos)
        .sort_index()
    )
    matriz.columns.name = None

    vazias = matriz.isna().stack()
    vazias = vazias[vazias].index.tolist()
    if vazias:
        raise ValueError(f"Mercado sem o produto no período (mercado, produto): {vazias}")
    return matriz


def ordenar_grupos(X, rotulos: np.ndarray) -> np.ndarray:
    """Renumera os grupos do mais barato (0) para o mais caro.

    A ordem é a média do preço relativo dos mercados de cada grupo, em todos
    os produtos. O K-Means numera os grupos de forma arbitrária; sem isso, o
    "grupo 0" de um período não teria relação com o "grupo 0" de outro.
    """
    X = np.asarray(X, dtype=float)
    rotulos = np.asarray(rotulos)
    grupos = np.unique(rotulos)
    nivel = {g: X[rotulos == g].mean() for g in grupos}
    nova_ordem = {g: i for i, g in enumerate(sorted(grupos, key=nivel.get))}
    return np.array([nova_ordem[g] for g in rotulos])


def ajustar_kmeans(X, k: int) -> KMeans:
    """Ajusta o K-Means com `k` grupos (`random_state=config.SEMENTE`)."""
    return KMeans(n_clusters=k, n_init=N_INICIALIZACOES, random_state=config.SEMENTE).fit(
        np.asarray(X, dtype=float)
    )


def curva_cotovelo(X, ks: range | None = None) -> pd.DataFrame:
    """Calcula a inércia (soma das distâncias ao quadrado até o centro do
    grupo) do K-Means para cada k. Usado no gráfico do cotovelo (aula 11)."""
    return pd.DataFrame(
        [{"k": k, "inercia": ajustar_kmeans(X, k).inertia_} for k in _faixa_k(ks)]
    )


def silhueta_por_k(X, ks: range | None = None) -> pd.DataFrame:
    """Calcula o coeficiente de silhueta médio para cada k (aula 12).

    Vai de -1 a 1; maior é melhor (mercados mais perto do próprio grupo do que
    do grupo vizinho).
    """
    X = np.asarray(X, dtype=float)
    return pd.DataFrame(
        [{"k": k, "silhueta": silhouette_score(X, ajustar_kmeans(X, k).labels_)} for k in _faixa_k(ks)]
    )


def indice_xie_beni(X, rotulos: np.ndarray, centros: np.ndarray) -> float:
    """Calcula o índice Xie-Beni de um agrupamento (aula 12). Menor é melhor.

    Versão para agrupamento rígido (K-Means):
        XB = soma(||x_i - c_{rótulo(i)}||^2) / (n * min_{j != l} ||c_j - c_l||^2)

    O numerador mede a compactação dos grupos e o denominador a separação
    entre os centros mais próximos.
    """
    X = np.asarray(X, dtype=float)
    centros = np.asarray(centros, dtype=float)
    rotulos = np.asarray(rotulos)
    if len(centros) < 2:
        raise ValueError("Xie-Beni precisa de pelo menos 2 grupos.")

    compactacao = ((X - centros[rotulos]) ** 2).sum()
    distancias = ((centros[:, None, :] - centros[None, :, :]) ** 2).sum(axis=2)
    separacao = distancias[~np.eye(len(centros), dtype=bool)].min()
    return float(compactacao / (len(X) * separacao))


def xie_beni_por_k(X, ks: range | None = None) -> pd.DataFrame:
    """Calcula o índice Xie-Beni do K-Means para cada k."""
    linhas = []
    for k in _faixa_k(ks):
        modelo = ajustar_kmeans(X, k)
        linhas.append({"k": k, "xie_beni": indice_xie_beni(X, modelo.labels_, modelo.cluster_centers_)})
    return pd.DataFrame(linhas)


def avaliar_k(X, ks: range | None = None) -> pd.DataFrame:
    """Junta cotovelo, silhueta e Xie-Beni numa tabela, uma linha por k."""
    return (
        curva_cotovelo(X, ks)
        .merge(silhueta_por_k(X, ks), on="k")
        .merge(xie_beni_por_k(X, ks), on="k")
    )


def indice_mercado(matriz: pd.DataFrame) -> pd.Series:
    """Resume cada mercado num número: a média do preço relativo nos produtos.

    0,90 = em média 10% mais barato que a mediana. Usado para ordenar os
    mercados e medir, por correlação de postos, se a ordem se mantém no tempo.
    """
    return matriz.mean(axis=1).rename("indice")


def preco_referencia_cesta(geral: pd.DataFrame, meses: int = config.MESES_PRECO_CESTA) -> pd.Series:
    """Preço geral de cada produto para converter a cesta em R$.

    Média do preço geral (mediana entre mercados) nos últimos `meses` meses da
    base, ou seja, o preço "de hoje" e não o de 2022 (decisão 11).
    """
    ultimos = sorted(geral["mes"].unique())[-meses:]
    return geral[geral["mes"].isin(ultimos)].groupby("produto")["preco"].mean()


def custo_cesta(relativos: pd.Series, precos_gerais: pd.Series, cesta: dict[str, float] | None = None) -> float:
    """Custo em R$ da cesta para um perfil de preço relativo.

    custo = soma(quantidade_p * preço_geral_p * relativo_p) nos produtos de
    `relativos` (os produtos fora dele, como o Pão Francês, não entram).
    """
    cesta = config.CESTA_DIEESE if cesta is None else cesta
    produtos = list(relativos.index)
    quantidades = pd.Series({p: cesta[p] for p in produtos})
    return float((quantidades * precos_gerais[produtos] * relativos).sum())


def custo_cesta_por_mercado(
    matriz: pd.DataFrame, precos_gerais: pd.Series, cesta: dict[str, float] | None = None
) -> pd.Series:
    """Custo em R$ da cesta em cada mercado (do mais barato ao mais caro)."""
    return matriz.apply(lambda linha: custo_cesta(linha, precos_gerais, cesta), axis=1).sort_values()


def economia_entre_grupos(
    matriz: pd.DataFrame,
    rotulos: np.ndarray,
    precos_gerais: pd.Series,
    cesta: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Estima quanto o consumidor economiza (em R$) escolhendo o grupo de mercados.

    Decisão 1 (Q3) + decisão 11: o perfil de cada grupo é a média do preço
    relativo dos seus mercados em cada produto; o custo da cesta do DIEESE
    nesse perfil é comparado com o custo na mediana (relativo = 1) e com o do
    grupo mais caro.

    Premissa: o preço relativo típico do mercado (mediana de todo o período)
    vale também para o preço de hoje (`preco_referencia_cesta`).

    Returns:
        Uma linha por grupo, com `n_mercados`, `indice_medio`, `custo_cesta`,
        a diferença para a mediana em R$ e em % e a economia em relação ao
        grupo mais caro (R$/mês e R$/ano).
    """
    rotulos = np.asarray(rotulos)
    custo_mediana = custo_cesta(pd.Series(1.0, index=matriz.columns), precos_gerais, cesta)

    linhas = []
    for grupo in sorted(np.unique(rotulos)):
        membros = matriz[rotulos == grupo]
        custo = custo_cesta(membros.mean(), precos_gerais, cesta)
        linhas.append({
            "grupo": grupo,
            "n_mercados": len(membros),
            "mercados": ", ".join(membros.index),
            "indice_medio": float(membros.to_numpy().mean()),
            "custo_cesta": custo,
            "dif_mediana_rs": custo - custo_mediana,
            "dif_mediana_pct": (custo / custo_mediana - 1) * 100,
        })
    tabela = pd.DataFrame(linhas)
    mais_caro = tabela["custo_cesta"].max()
    tabela["economia_vs_mais_caro_rs_mes"] = mais_caro - tabela["custo_cesta"]
    tabela["economia_vs_mais_caro_rs_ano"] = tabela["economia_vs_mais_caro_rs_mes"] * 12
    return tabela


def grupos_por_periodo(
    relativo: pd.DataFrame,
    k: int,
    periodos: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Agrupa os mercados em cada período e devolve os grupos lado a lado.

    Uma linha por mercado; a coluna `completo` é o agrupamento com todo o
    período e há uma coluna por período ("AAAA-MM a AAAA-MM"). Os rótulos já
    vêm ordenados (0 = grupo mais barato), então são comparáveis entre colunas.
    """
    periodos = config.PERIODOS_ESTABILIDADE if periodos is None else periodos
    matrizes = {"completo": montar_matriz_mercados(relativo)}
    for inicio, fim in periodos:
        matrizes[f"{inicio} a {fim}"] = montar_matriz_mercados(relativo, inicio=inicio, fim=fim)

    mercados = matrizes["completo"].index
    colunas = {}
    for nome, matriz in matrizes.items():
        if not matriz.index.equals(mercados):
            raise ValueError(f"Período {nome} não tem os mesmos mercados do período completo.")
        colunas[nome] = ordenar_grupos(matriz, ajustar_kmeans(matriz, k).labels_)
    return pd.DataFrame(colunas, index=mercados)


def estabilidade_temporal(
    relativo: pd.DataFrame,
    k: int,
    periodos: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Verifica se os grupos se mantêm estáveis no tempo.

    Decisão 4: agrupa os mercados separadamente em cada período e compara com
    o agrupamento do período completo e com o período anterior. Se o mercado
    barato de 2023 virou caro em 2025, a recomendação não se sustenta.

    Medidas, por período:
    - `ari_vs_completo` / `ari_vs_anterior`: adjusted Rand index (1 = mesmos
      grupos; ~0 = concordância de acaso). Não depende da numeração dos grupos.
    - `pct_mesmo_grupo`: % de mercados no mesmo grupo (ordenado por preço) que
      no período completo.
    - `spearman_indice`: correlação de postos entre o índice de preço dos
      mercados no período e no período completo (1 = mesma ordem do mais
      barato ao mais caro). Não depende do K-Means.
    """
    periodos = config.PERIODOS_ESTABILIDADE if periodos is None else periodos
    grupos = grupos_por_periodo(relativo, k, periodos)
    indice_completo = indice_mercado(montar_matriz_mercados(relativo))

    linhas = []
    anterior = None
    for inicio, fim in periodos:
        nome = f"{inicio} a {fim}"
        indice = indice_mercado(montar_matriz_mercados(relativo, inicio=inicio, fim=fim))
        linhas.append({
            "periodo": nome,
            "ari_vs_completo": adjusted_rand_score(grupos["completo"], grupos[nome]),
            "ari_vs_anterior": np.nan if anterior is None else adjusted_rand_score(grupos[anterior], grupos[nome]),
            "pct_mesmo_grupo": float((grupos["completo"] == grupos[nome]).mean() * 100),
            "spearman_indice": float(spearmanr(indice_completo, indice[indice_completo.index]).statistic),
        })
        anterior = nome
    return pd.DataFrame(linhas)
