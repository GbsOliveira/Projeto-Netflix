import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração visual
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [4, 5]

# 1. Carga e Limpeza Inicial
tabela = pd.read_csv("cancelamentos.csv")

# Remover coluna que não agrega valor estatístico
if "CustomerID" in tabela.columns:
    tabela = tabela.drop("CustomerID", axis=1)

# Remover valores nulos
tabela = tabela.dropna()

# 2. Padronização de contratos
mapa_contratos = {"Annual": "Anual",
                  "Quarterly": "Trimestral", "Monthly": "Mensal"}
tabela["duracao_contrato"] = (
    tabela["duracao_contrato"].str.title()
    .map(mapa_contratos)
    .fillna(tabela["duracao_contrato"])
)

# Frequência de contratos
print(tabela["duracao_contrato"].value_counts())
tabela["duracao_contrato"].value_counts().plot(
    kind="bar", title="Duração do contrato")
plt.show()

# 3. Correlação entre variáveis numéricas
plt.figure(figsize=(12, 8))
sns.heatmap(
    tabela.select_dtypes(include=["number"]).corr(),
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)
plt.title("Correlação entre Variáveis de Cancelamento")
plt.show()

# 4. Relação entre atraso e cancelamento
plt.figure()
sns.boxplot(data=tabela, x="cancelou", y="dias_atraso")
plt.title("Relação entre Dias de Atraso e Cancelamento")
plt.show()

# 5. Função para taxa de cancelamento


def plot_taxa_cancelamento(df, coluna, titulo):
    taxa = df.groupby(coluna)["cancelou"].mean().reset_index()
    taxa["cancelou"] = taxa["cancelou"] * 100

    plt.figure()
    ax = sns.barplot(data=taxa, x=coluna, y="cancelou", palette="viridis")
    ax.set_title(titulo)
    ax.set_ylabel("Taxa de Cancelamento (%)")
    plt.show()


# Chamando a função para insights principais
plot_taxa_cancelamento(tabela, "duracao_contrato",
                       "Cancelamento por Tipo de Contrato")

# 6. Análise de ligações ao call center
ax = sns.barplot(data=tabela, x="cancelou",
                 y="ligacoes_callcenter", estimator="mean")
ax.set_title("Influência do Call Center na Taxa de Cancelamento")
plt.show()

# Categorizar número de ligações em bins
bins = [-1, 0, 2, 5, tabela["ligacoes_callcenter"].max()]
labels = ["0", "1-2", "3-5", "6+"]
tabela["ligacoes_bin"] = pd.cut(
    tabela["ligacoes_callcenter"], bins=bins, labels=labels)

# Taxa de cancelamento por contrato e ligações
taxa_calls = tabela.groupby(["duracao_contrato", "ligacoes_bin"])[
    "cancelou"].mean().reset_index()
taxa_calls["cancelou"] = taxa_calls["cancelou"] * 100

ax = sns.barplot(data=taxa_calls, x="duracao_contrato",
                 y="cancelou", hue="ligacoes_bin")
ax.set_title(
    "Ligações no call center sobre a taxa de cancelamento")
ax.set_ylabel("Taxa de cancelamento (%)")
ax.set_xlabel("Duração do contrato")
plt.legend(title="Ligações")
plt.tight_layout()
plt.show()

# 7. Conclusão da Análise de Negócio
print(tabela["cancelou"].value_counts(normalize=True).map("{:.2%}".format))

# 8. Taxa de cancelamento por dias de atraso
taxa_atraso = tabela.groupby("dias_atraso")["cancelou"].mean().reset_index()
taxa_atraso["cancelou"] = taxa_atraso["cancelou"] * 100

plt.figure(figsize=(10, 5))
sns.lineplot(data=taxa_atraso, x="dias_atraso", y="cancelou", marker="o")
plt.title("Taxa de Cancelamento por Dias de Atraso")
plt.axhline(50, color="red", linestyle="--", label="Ponto Crítico (50%)")
plt.ylabel("Taxa de Cancelamento (%)")
plt.xlabel("Dias de Atraso")
plt.grid(True)
plt.show()

# 9. Análise por faixas de atraso
max_atraso = tabela["dias_atraso"].dropna().max()
bins_atraso = [-1, 5, 10, 15, 20, max_atraso]
labels_atraso = ["Até 5 dias", "6-10 dias",
                 "11-15 dias", "16-20 dias", "Mais de 20"]

tabela["faixa_atraso"] = pd.cut(
    tabela["dias_atraso"], bins=bins_atraso, labels=labels_atraso)

taxa_faixa = tabela.groupby("faixa_atraso", observed=False)[
    "cancelou"].mean().reset_index()
taxa_faixa["cancelou"] = taxa_faixa["cancelou"] * 100

plt.figure(figsize=(10, 5))
sns.barplot(data=taxa_faixa, x="faixa_atraso", y="cancelou", palette="viridis")
plt.title("Taxa de Cancelamento por Faixa de Atraso")
plt.ylabel("Taxa de Cancelamento (%)")
plt.show()
