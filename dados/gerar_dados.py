import pandas as pd
import numpy as np
from datetime import date, timedelta
import random, os

random.seed(42)
np.random.seed(42)

OUT = "/home/claude/AurumCap/dados"

# --- Marcas do Grupo ---
marcas = [
    {"id": 1, "nome": "AurumCap Banca", "setor": "Banca de Retalho", "fundacao": 2001},
    {"id": 2, "nome": "AurumCap Seguros", "setor": "Seguros", "fundacao": 2005},
    {"id": 3, "nome": "AurumCap Investimentos", "setor": "Gestao de Ativos", "fundacao": 2010},
]
pd.DataFrame(marcas).to_csv(f"{OUT}/marcas.csv", index=False)

# --- Clientes ---
nomes = ["Ana Silva","Rui Costa","Maria Ferreira","Joao Santos","Carlos Oliveira",
         "Ines Rodrigues","Pedro Martins","Sofia Sousa","Miguel Lopes","Beatriz Pinto",
         "Luis Carvalho","Catarina Alves","Nuno Pereira","Filipa Gomes","Tiago Ribeiro",
         "Mariana Fernandes","Andre Correia","Claudia Marques","Bruno Vieira","Leonor Cruz",
         "Paulo Moreira","Rita Barros","Diogo Teixeira","Marta Cunha","Goncalo Monteiro",
         "Helena Fonseca","Sergio Rocha","Vanessa Cardoso","Frederico Lima","Joana Borges",
         "Empresa XYZ Lda","Construtora ABC SA","Tech Solutions Lda","Retail Group SA",
         "Farmacias Norte Lda","Auto Pecas Sul SA","Logistica Central Lda","Hotel Atlantico SA",
         "Clinica Saude Lda","Media Digital SA","Imobiliaria Prata Lda","Exportadora PT SA"]

cidades = ["Lisboa","Porto","Braga","Coimbra","Aveiro","Faro","Setubal","Leiria","Viseu","Evora"]
segmentos = ["Particular","PME","Corporate","Private Banking"]
seg_pesos = [0.55, 0.25, 0.12, 0.08]

clientes = []
for i, nome in enumerate(nomes):
    seg = np.random.choice(segmentos, p=seg_pesos)
    marca_ids = random.sample([1,2,3], k=random.randint(1,3))
    for mid in marca_ids:
        clientes.append({
            "cliente_id": f"C{i+1:04d}",
            "nome": nome,
            "cidade": random.choice(cidades),
            "segmento": seg,
            "marca_id": mid,
            "data_adesao": date(random.randint(2021,2022), random.randint(1,12), random.randint(1,28)).isoformat(),
            "ativo": random.choice([True, True, True, False])
        })
pd.DataFrame(clientes).to_csv(f"{OUT}/clientes.csv", index=False)

# --- Produtos Financeiros ---
produtos = [
    {"produto_id":"P001","nome":"Conta Corrente Premium","marca_id":1,"tipo":"Deposito","margem_pct":1.2},
    {"produto_id":"P002","nome":"Credito Habitacao","marca_id":1,"tipo":"Credito","margem_pct":3.5},
    {"produto_id":"P003","nome":"Credito Pessoal","marca_id":1,"tipo":"Credito","margem_pct":8.2},
    {"produto_id":"P004","nome":"Deposito a Prazo 5pct","marca_id":1,"tipo":"Deposito","margem_pct":2.1},
    {"produto_id":"P005","nome":"Cartao Platinum","marca_id":1,"tipo":"Cartao","margem_pct":5.8},
    {"produto_id":"P006","nome":"Seguro Vida Premium","marca_id":2,"tipo":"Seguro Vida","margem_pct":22.0},
    {"produto_id":"P007","nome":"Seguro Automovel","marca_id":2,"tipo":"Seguro Auto","margem_pct":18.5},
    {"produto_id":"P008","nome":"Seguro Habitacao","marca_id":2,"tipo":"Seguro Habitacao","margem_pct":20.0},
    {"produto_id":"P009","nome":"Seguro Saude Empresarial","marca_id":2,"tipo":"Seguro Saude","margem_pct":25.0},
    {"produto_id":"P010","nome":"Fundo Acoes PT","marca_id":3,"tipo":"Fundo","margem_pct":1.5},
    {"produto_id":"P011","nome":"Fundo Obrigacoes Europa","marca_id":3,"tipo":"Fundo","margem_pct":0.8},
    {"produto_id":"P012","nome":"Fundo Imobiliario","marca_id":3,"tipo":"Fundo","margem_pct":2.0},
    {"produto_id":"P013","nome":"Carteira Discricionaria","marca_id":3,"tipo":"Gestao","margem_pct":1.2},
    {"produto_id":"P014","nome":"PPR Reforma 2050","marca_id":3,"tipo":"Poupanca","margem_pct":1.0},
]
pd.DataFrame(produtos).to_csv(f"{OUT}/produtos.csv", index=False)

# --- Transacoes (Jan 2022 - Dez 2024) ---
start = date(2022, 1, 1)
end   = date(2024, 12, 31)
delta = (end - start).days

transacoes = []
tid = 1
for _ in range(2800):
    d   = start + timedelta(days=random.randint(0, delta))
    cli = random.choice(clientes)
    prods_marca = [p for p in produtos if p["marca_id"] == cli["marca_id"]]
    if not prods_marca:
        continue
    prod = random.choice(prods_marca)

    base_vals = {
        "Deposito":  (500, 50000), "Credito": (5000, 250000),
        "Cartao":    (200, 5000),  "Seguro Vida": (800, 4000),
        "Seguro Auto": (400, 1800),"Seguro Habitacao": (600, 2500),
        "Seguro Saude": (1500, 8000),"Fundo": (1000, 100000),
        "Gestao":    (50000, 500000),"Poupanca": (2000, 30000),
    }
    lo, hi = base_vals.get(prod["tipo"], (1000, 10000))
    valor  = round(random.uniform(lo, hi), 2)
    receita = round(valor * prod["margem_pct"] / 100, 2)

    mes = d.month
    mult = 1.0 + (0.15 if mes in [10,11,12] else 0.05 if mes in [7,8] else 0)
    receita = round(receita * mult, 2)

    transacoes.append({
        "transacao_id": f"T{tid:05d}",
        "data":          d.isoformat(),
        "ano":           d.year,
        "mes":           d.month,
        "trimestre":     f"Q{(d.month-1)//3+1}",
        "cliente_id":    cli["cliente_id"],
        "marca_id":      cli["marca_id"],
        "produto_id":    prod["produto_id"],
        "tipo_produto":  prod["tipo"],
        "valor_contrato":valor,
        "receita":       receita,
        "cidade":        cli["cidade"],
        "segmento":      cli["segmento"],
    })
    tid += 1

df_t = pd.DataFrame(transacoes).sort_values("data")
df_t.to_csv(f"{OUT}/transacoes.csv", index=False)

# --- KPIs Mensais por Marca ---
kpis = []
for ano in [2022, 2023, 2024]:
    for mes in range(1, 13):
        for m in marcas:
            sub = df_t[(df_t.ano==ano)&(df_t.mes==mes)&(df_t.marca_id==m["id"])]
            receita = sub.receita.sum()
            base_custo = {1: 0.62, 2: 0.55, 3: 0.48}[m["id"]]
            custo   = round(receita * (base_custo + np.random.uniform(-0.03, 0.03)), 2)
            lucro   = round(receita - custo, 2)
            kpis.append({
                "ano": ano, "mes": mes,
                "periodo": f"{ano}-{mes:02d}",
                "marca_id": m["id"],
                "marca_nome": m["nome"],
                "receita": round(receita, 2),
                "custos":  custo,
                "lucro_bruto": lucro,
                "margem_pct": round(lucro/receita*100, 1) if receita else 0,
                "num_transacoes": len(sub),
                "clientes_ativos": sub.cliente_id.nunique(),
                "aum": round(sub[sub.tipo_produto.isin(["Fundo","Gestao","Poupanca"])].valor_contrato.sum(), 2),
            })
pd.DataFrame(kpis).to_csv(f"{OUT}/kpis_mensais.csv", index=False)

print("Dados gerados:")
print(f"  clientes.csv      -> {len(clientes)} registos")
print(f"  produtos.csv      -> {len(produtos)} produtos")
print(f"  transacoes.csv    -> {len(df_t)} transacoes")
print(f"  kpis_mensais.csv  -> {len(kpis)} registos")
