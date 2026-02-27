"""
AurumCap Grupo Financeiro — Análise de Dados Completa
====================================================
Script principal de análise: carrega dados, calcula KPIs,
gera visualizações profissionais e exporta relatório Excel.

Execução: python3 analise_aurumcap.py
Outputs:  ../graficos/  e  ../excel/dashboard_aurumcap.xlsx
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Configuração ──────────────────────────────────────────────────────────
BASE    = Path(__file__).parent.parent
DADOS   = BASE / "dados"
GRAF    = BASE / "graficos"
EXCEL   = BASE / "excel"
GRAF.mkdir(exist_ok=True)
EXCEL.mkdir(exist_ok=True)

# Paleta de cores institucional
CORES = {
    "AurumCap Banca":         "#1B3F7A",
    "AurumCap Seguros":       "#0E7A6E",
    "AurumCap Investimentos": "#B8860B",
    "grupo":                 "#2C2C54",
    "fundo":                 "#F4F6F9",
    "destaque":              "#E63946",
}
ANOS = [2022, 2023, 2024]

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "figure.facecolor": "white",
    "axes.facecolor":   "#F4F6F9",
    "axes.grid":        True,
    "grid.color":       "white",
    "grid.linewidth":   1.2,
    "axes.spines.top":  False,
    "axes.spines.right":False,
})

# ── Carregamento de Dados ─────────────────────────────────────────────────
print("A carregar dados...")
df_t  = pd.read_csv(DADOS / "transacoes.csv",   parse_dates=["data"])
df_k  = pd.read_csv(DADOS / "kpis_mensais.csv")
df_m  = pd.read_csv(DADOS / "marcas.csv")
df_p  = pd.read_csv(DADOS / "produtos.csv")
df_c  = pd.read_csv(DADOS / "clientes.csv")
print(f"  {len(df_t):,} transacoes | {len(df_k)} KPIs mensais | {len(df_c)} clientes")

# ── KPIs Globais ──────────────────────────────────────────────────────────
receita_total  = df_k.receita.sum()
lucro_total    = df_k.lucro_bruto.sum()
margem_media   = df_k.margem_pct.mean()
total_trans    = df_t.shape[0]
clientes_uniq  = df_t.cliente_id.nunique()

print(f"\n{'='*55}")
print(f"  NOVACAP GRUPO FINANCEIRO — KPIs 2022-2024")
print(f"{'='*55}")
print(f"  Receita Total:   €{receita_total:>12,.0f}")
print(f"  Lucro Total:     €{lucro_total:>12,.0f}")
print(f"  Margem Média:    {margem_media:>11.1f}%")
print(f"  Transações:      {total_trans:>12,}")
print(f"  Clientes Únicos: {clientes_uniq:>12,}")
print(f"{'='*55}\n")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 1 — Receita Anual por Marca (Barras Agrupadas)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor("white")

pivot = df_k.groupby(["ano","marca_nome"])["receita"].sum().unstack()
marcas_ord = pivot.columns.tolist()
x = np.arange(len(ANOS))
width = 0.26

for i, marca in enumerate(marcas_ord):
    vals = [pivot.loc[a, marca] if a in pivot.index else 0 for a in ANOS]
    bars = ax.bar(x + i*width - width, vals, width, label=marca,
                  color=CORES.get(marca,"#555"), alpha=0.9, zorder=3)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+200,
                f"€{val/1e3:.0f}k", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

ax.set_xticks(x)
ax.set_xticklabels([str(a) for a in ANOS], fontsize=12)
ax.set_title("Receita Anual por Marca — AurumCap Grupo", fontsize=14, fontweight="bold", pad=15)
ax.set_ylabel("Receita (€)", fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"€{x/1e3:.0f}k"))
ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax.set_facecolor("#F8F9FA")
plt.tight_layout()
plt.savefig(GRAF/"01_receita_anual_marca.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 1 guardado: receita anual por marca")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 2 — Evolução Mensal da Receita do Grupo (2022-2024)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 5.5))
fig.patch.set_facecolor("white")

rec_mensal = df_k.groupby(["ano","mes"])["receita"].sum().reset_index()
rec_mensal["periodo_n"] = (rec_mensal["ano"] - 2022)*12 + rec_mensal["mes"]

cores_anos = {2022: "#8EC5FC", 2023: "#3A7BD5", 2024: "#1B3F7A"}
for ano in ANOS:
    sub = rec_mensal[rec_mensal.ano==ano].sort_values("mes")
    ax.plot(sub.mes + (ano-2022)*12, sub.receita, marker="o", markersize=4,
            linewidth=2.5, label=str(ano), color=cores_anos[ano], zorder=3)

# marcas x-axis
xticks = list(range(1,37))
xlabels = []
for i in range(36):
    m = (i % 12) + 1
    xlabels.append(f"{'JFMAMJJASOND'[m-1]}")

ax.set_xticks(xticks[::1])
ax.set_xticklabels(xlabels, fontsize=7)
ax.set_title("Evolução Mensal da Receita Consolidada do Grupo (2022–2024)",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("Receita Mensal (€)", fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"€{x/1e3:.0f}k"))
ax.legend(fontsize=10, loc="upper left")
ax.set_facecolor("#F8F9FA")

# separadores de ano
for sep in [12.5, 24.5]:
    ax.axvline(sep, color="#cccccc", linestyle="--", linewidth=1, zorder=1)
for ano, pos in zip(ANOS, [6.5, 18.5, 30.5]):
    ax.text(pos, ax.get_ylim()[0], str(ano), ha="center", fontsize=9,
            color=cores_anos[ano], fontweight="bold")

plt.tight_layout()
plt.savefig(GRAF/"02_evolucao_mensal.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 2 guardado: evolução mensal")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 3 — Margem de Lucro por Marca e Ano (Heatmap)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 4.5))
fig.patch.set_facecolor("white")

heat_data = df_k.groupby(["marca_nome","ano"])["margem_pct"].mean().unstack()
sns.heatmap(heat_data, annot=True, fmt=".1f", cmap="YlOrRd",
            linewidths=0.5, linecolor="white", ax=ax,
            cbar_kws={"label":"Margem %", "shrink":0.8})
ax.set_title("Margem de Lucro Bruto por Marca e Ano (%)",
             fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("")
ax.set_xlabel("")
plt.tight_layout()
plt.savefig(GRAF/"03_heatmap_margem.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 3 guardado: heatmap margem")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 4 — Mix de Receita por Tipo de Produto (Donut)
# ═══════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(14, 5.5))
fig.patch.set_facecolor("white")
fig.suptitle("Mix de Receita por Tipo de Produto — Por Marca (2022-2024)",
             fontsize=13, fontweight="bold", y=1.01)

cores_tipos = ["#1B3F7A","#0E7A6E","#B8860B","#E63946","#6C5CE7",
               "#00B894","#FDCB6E","#74B9FF","#A29BFE","#FD79A8"]

for ax, (mid, marca_nome) in zip(axes, [(1,"AurumCap Banca"),(2,"AurumCap Seguros"),(3,"AurumCap Investimentos")]):
    sub = df_t[df_t.marca_id==mid].groupby("tipo_produto")["receita"].sum()
    sub = sub.sort_values(ascending=False)
    wedges, texts, autotexts = ax.pie(
        sub.values, labels=None, autopct="%1.1f%%",
        colors=cores_tipos[:len(sub)], startangle=90,
        wedgeprops={"linewidth":2, "edgecolor":"white"},
        pctdistance=0.82
    )
    for at in autotexts:
        at.set_fontsize(8)
    # anel central
    centro = plt.Circle((0,0), 0.55, color="white")
    ax.add_artist(centro)
    ax.text(0, 0, marca_nome.replace("AurumCap ",""), ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#333")
    ax.legend(sub.index, loc="lower center", fontsize=7,
              bbox_to_anchor=(0.5,-0.22), ncol=2)
    ax.set_title(marca_nome, fontsize=10, fontweight="bold", pad=8)

plt.tight_layout()
plt.savefig(GRAF/"04_mix_produto.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 4 guardado: mix produto")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 5 — Receita por Cidade (Top 8)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor("white")

cidade_rec = df_t.groupby("cidade")["receita"].sum().sort_values(ascending=True).tail(8)
cores_bar  = [CORES["grupo"] if i < len(cidade_rec)-1 else CORES["destaque"]
              for i in range(len(cidade_rec))]
bars = ax.barh(cidade_rec.index, cidade_rec.values, color=cores_bar, alpha=0.9, zorder=3)
for bar, val in zip(bars, cidade_rec.values):
    ax.text(val + 500, bar.get_y()+bar.get_height()/2,
            f"€{val/1e3:.1f}k", va="center", fontsize=9, fontweight="bold")

ax.set_title("Receita por Cidade — Top 8 (2022–2024)", fontsize=13, fontweight="bold", pad=12)
ax.set_xlabel("Receita Total (€)", fontsize=10)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"€{x/1e3:.0f}k"))
ax.set_facecolor("#F8F9FA")
plt.tight_layout()
plt.savefig(GRAF/"05_receita_cidade.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 5 guardado: receita por cidade")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 6 — KPI Cards 2024 (Resumo Visual)
# ═══════════════════════════════════════════════════════════════
df_2024 = df_k[df_k.ano==2024]
kpis_2024 = {
    "Receita\nTotal":       f"€{df_2024.receita.sum()/1e3:.0f}k",
    "Lucro\nBruto":         f"€{df_2024.lucro_bruto.sum()/1e3:.0f}k",
    "Margem\nMédia":        f"{df_2024.margem_pct.mean():.1f}%",
    "Transações\n2024":     f"{df_2024.num_transacoes.sum():,}",
    "Clientes\nAtivos":     f"{df_2024.clientes_ativos.sum():,}",
    "AUM\nInvestimentos":   f"€{df_2024.aum.sum()/1e6:.1f}M",
}

fig, axes = plt.subplots(1, 6, figsize=(16, 3))
fig.patch.set_facecolor("white")
fig.suptitle("AurumCap Grupo — KPIs 2024", fontsize=14, fontweight="bold", y=1.05)

card_cores = ["#1B3F7A","#0E7A6E","#B8860B","#6C5CE7","#E63946","#00B894"]
for ax, (label, val), cor in zip(axes, kpis_2024.items(), card_cores):
    ax.set_facecolor(cor)
    ax.text(0.5, 0.65, val, ha="center", va="center", fontsize=18,
            fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.2, label, ha="center", va="center", fontsize=9,
            color="white", alpha=0.88, transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

plt.tight_layout()
plt.savefig(GRAF/"06_kpi_cards_2024.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 6 guardado: KPI cards 2024")


# ═══════════════════════════════════════════════════════════════
# GRÁFICO 7 — Crescimento YoY por Marca
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor("white")

rec_ano = df_k.groupby(["marca_nome","ano"])["receita"].sum().reset_index()
yoy_data = []
for marca in rec_ano.marca_nome.unique():
    sub = rec_ano[rec_ano.marca_nome==marca].sort_values("ano")
    for i in range(1, len(sub)):
        r0 = sub.iloc[i-1].receita
        r1 = sub.iloc[i].receita
        yoy_data.append({
            "marca": marca,
            "ano": sub.iloc[i].ano,
            "yoy_pct": (r1-r0)/r0*100
        })
df_yoy = pd.DataFrame(yoy_data)

x = np.arange(len([2023,2024]))
width = 0.26
for i, marca in enumerate(df_yoy.marca.unique()):
    sub = df_yoy[df_yoy.marca==marca].sort_values("ano")
    bars = ax.bar(x + i*width - width, sub.yoy_pct, width, label=marca,
                  color=CORES.get(marca,"#555"), alpha=0.9, zorder=3)
    for bar, val in zip(bars, sub.yoy_pct):
        ax.text(bar.get_x()+bar.get_width()/2,
                bar.get_height() + (0.3 if val>=0 else -1.2),
                f"{val:+.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.axhline(0, color="#999", linewidth=1)
ax.set_xticks(x)
ax.set_xticklabels(["2023 vs 2022","2024 vs 2023"], fontsize=11)
ax.set_title("Crescimento Anual (YoY) por Marca", fontsize=13, fontweight="bold", pad=12)
ax.set_ylabel("Variação (%)", fontsize=10)
ax.legend(fontsize=9)
ax.set_facecolor("#F8F9FA")
plt.tight_layout()
plt.savefig(GRAF/"07_crescimento_yoy.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Gráfico 7 guardado: crescimento YoY")


# ═══════════════════════════════════════════════════════════════
# EXPORT EXCEL — Dashboard com múltiplos separadores
# ═══════════════════════════════════════════════════════════════
print("\nA exportar Excel...")

with pd.ExcelWriter(EXCEL/"dashboard_aurumcap.xlsx", engine="openpyxl") as writer:

    # Sheet 1: KPIs Mensais
    df_k.to_excel(writer, sheet_name="KPIs Mensais", index=False)

    # Sheet 2: Transações completas
    df_t.to_excel(writer, sheet_name="Transacoes", index=False)

    # Sheet 3: Resumo por Marca e Ano
    resumo = df_k.groupby(["marca_nome","ano"]).agg(
        receita=("receita","sum"),
        custos=("custos","sum"),
        lucro=("lucro_bruto","sum"),
        margem_pct=("margem_pct","mean"),
        transacoes=("num_transacoes","sum"),
        clientes=("clientes_ativos","sum"),
        aum=("aum","sum")
    ).round(2).reset_index()
    resumo.to_excel(writer, sheet_name="Resumo Marca-Ano", index=False)

    # Sheet 4: Receita por Cidade
    cidade_df = df_t.groupby(["cidade","ano"])["receita"].sum().round(2).reset_index()
    cidade_df.to_excel(writer, sheet_name="Geografico", index=False)

    # Sheet 5: Mix de Produto
    mix_df = df_t.groupby(["tipo_produto","marca_id"])["receita"].sum().round(2).reset_index()
    mix_df.to_excel(writer, sheet_name="Mix Produto", index=False)

    # Sheet 6: Top Clientes
    top_cli = df_t.groupby(["cliente_id","segmento"]).agg(
        contratos=("transacao_id","count"),
        receita=("receita","sum"),
        valor_total=("valor_contrato","sum")
    ).round(2).reset_index().sort_values("receita", ascending=False).head(20)
    top_cli.to_excel(writer, sheet_name="Top Clientes", index=False)

    # Sheet 7: YoY Analysis
    yoy_full = df_k.groupby(["marca_nome","ano"])["receita"].sum().unstack().round(2)
    yoy_full["YoY 2022-2023 (%)"] = ((yoy_full[2023]-yoy_full[2022])/yoy_full[2022]*100).round(1)
    yoy_full["YoY 2023-2024 (%)"] = ((yoy_full[2024]-yoy_full[2023])/yoy_full[2023]*100).round(1)
    yoy_full.reset_index().to_excel(writer, sheet_name="YoY Analysis", index=False)

print("  Excel guardado: dashboard_aurumcap.xlsx")
print(f"\nAnalise completa!")
print(f"  Graficos: {GRAF}")
print(f"  Excel:    {EXCEL}")
