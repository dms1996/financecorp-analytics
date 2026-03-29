-- ============================================================
-- NOVACAP GRUPO FINANCEIRO — Queries Analíticas
-- 20 queries prontas para análise de negócio
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- Q01 · Receita Total por Marca e Ano
-- ────────────────────────────────────────────────────────────
SELECT
    m.nome                          AS marca,
    k.ano,
    SUM(k.receita)                  AS receita_total,
    SUM(k.lucro_bruto)              AS lucro_total,
    ROUND(AVG(k.margem_pct), 1)    AS margem_media_pct,
    SUM(k.num_transacoes)          AS total_transacoes
FROM fact_kpis_mensais k
JOIN dim_marcas m ON k.marca_id = m.marca_id
GROUP BY m.nome, k.ano
ORDER BY k.ano, receita_total DESC;

-- ────────────────────────────────────────────────────────────
-- Q02 · Crescimento Anual (YoY) por Marca
-- ────────────────────────────────────────────────────────────
WITH receita_anual AS (
    SELECT marca_id, ano, SUM(receita) AS receita
    FROM fact_kpis_mensais
    GROUP BY marca_id, ano
)
SELECT
    m.nome                                          AS marca,
    r1.ano,
    r1.receita                                      AS receita_atual,
    r0.receita                                      AS receita_ano_anterior,
    ROUND((r1.receita - r0.receita) / r0.receita * 100, 1) AS crescimento_yoy_pct
FROM receita_anual r1
LEFT JOIN receita_anual r0 ON r1.marca_id = r0.marca_id AND r1.ano = r0.ano + 1
JOIN dim_marcas m ON r1.marca_id = m.marca_id
WHERE r0.receita IS NOT NULL
ORDER BY r1.ano, m.nome;

-- ────────────────────────────────────────────────────────────
-- Q03 · Receita Mensal do Grupo (todos os meses, todas as marcas)
-- ────────────────────────────────────────────────────────────
SELECT
    periodo,
    ano,
    mes,
    SUM(receita)        AS receita_grupo,
    SUM(lucro_bruto)    AS lucro_grupo,
    SUM(num_transacoes) AS transacoes_total,
    ROUND(SUM(lucro_bruto) / SUM(receita) * 100, 1) AS margem_grupo_pct
FROM fact_kpis_mensais
GROUP BY periodo, ano, mes
ORDER BY periodo;

-- ────────────────────────────────────────────────────────────
-- Q04 · Top 10 Produtos por Receita
-- ────────────────────────────────────────────────────────────
SELECT
    p.produto_id,
    p.nome                          AS produto,
    p.tipo,
    m.nome                          AS marca,
    COUNT(t.transacao_id)           AS num_vendas,
    ROUND(SUM(t.valor_contrato), 2) AS volume_contratado,
    ROUND(SUM(t.receita), 2)        AS receita_total,
    ROUND(AVG(t.receita), 2)        AS receita_media,
    RANK() OVER (ORDER BY SUM(t.receita) DESC) AS ranking
FROM fact_transacoes t
JOIN dim_produtos p ON t.produto_id = p.produto_id
JOIN dim_marcas m ON t.marca_id = m.marca_id
GROUP BY p.produto_id, p.nome, p.tipo, m.nome
ORDER BY receita_total DESC
LIMIT 10;

-- ────────────────────────────────────────────────────────────
-- Q05 · Análise por Segmento de Cliente
-- ────────────────────────────────────────────────────────────
SELECT
    t.segmento,
    t.ano                                   AS ano,
    COUNT(DISTINCT t.cliente_id)            AS clientes_unicos,
    COUNT(t.transacao_id)                   AS num_transacoes,
    ROUND(SUM(t.receita), 2)               AS receita_total,
    ROUND(AVG(t.receita), 2)               AS receita_media_por_transacao,
    ROUND(SUM(t.receita) / COUNT(DISTINCT t.cliente_id), 2) AS receita_por_cliente
FROM fact_transacoes t
JOIN dim_calendario c ON t.data_key = c.data_key
GROUP BY t.segmento, t.ano
ORDER BY t.ano, receita_total DESC;

-- ────────────────────────────────────────────────────────────
-- Q06 · Análise Geográfica — Receita por Cidade
-- ────────────────────────────────────────────────────────────
SELECT
    t.cidade,
    COUNT(DISTINCT t.cliente_id)   AS clientes,
    COUNT(t.transacao_id)          AS transacoes,
    ROUND(SUM(t.receita), 2)       AS receita_total,
    RANK() OVER (ORDER BY SUM(t.receita) DESC) AS ranking_cidade
FROM fact_transacoes t
GROUP BY t.cidade
ORDER BY receita_total DESC;

-- ────────────────────────────────────────────────────────────
-- Q07 · Receita Acumulada YTD (Running Total) por Marca
-- ────────────────────────────────────────────────────────────
SELECT
    m.nome                  AS marca,
    k.periodo,
    k.receita               AS receita_mes,
    SUM(k.receita) OVER (
        PARTITION BY k.marca_id, k.ano
        ORDER BY k.mes
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                       AS receita_ytd
FROM fact_kpis_mensais k
JOIN dim_marcas m ON k.marca_id = m.marca_id
ORDER BY k.marca_id, k.ano, k.mes;

-- ────────────────────────────────────────────────────────────
-- Q08 · Sazonalidade — Receita por Trimestre
-- ────────────────────────────────────────────────────────────
SELECT
    c.ano,
    c.trimestre,
    m.nome                          AS marca,
    ROUND(SUM(t.receita), 2)       AS receita,
    COUNT(t.transacao_id)          AS transacoes,
    ROUND(AVG(t.receita), 2)       AS ticket_medio
FROM fact_transacoes t
JOIN dim_calendario c ON t.data_key = c.data_key
JOIN dim_marcas m ON t.marca_id = m.marca_id
GROUP BY c.ano, c.trimestre, m.nome
ORDER BY c.ano, c.trimestre, m.nome;

-- ────────────────────────────────────────────────────────────
-- Q09 · Clientes com Maior Valor (Top 15)
-- ────────────────────────────────────────────────────────────
SELECT
    c.cliente_id,
    c.nome,
    c.segmento,
    m.nome                          AS marca,
    COUNT(t.transacao_id)          AS num_contratos,
    ROUND(SUM(t.valor_contrato), 2) AS volume_total,
    ROUND(SUM(t.receita), 2)       AS receita_gerada,
    ROUND(AVG(t.receita), 2)       AS receita_media,
    MAX(t.data_key)                AS ultima_transacao
FROM fact_transacoes t
JOIN dim_clientes c ON t.cliente_id = c.cliente_id
JOIN dim_marcas m ON t.marca_id = m.marca_id
GROUP BY c.cliente_id, c.nome, c.segmento, m.nome
ORDER BY receita_gerada DESC
LIMIT 15;

-- ────────────────────────────────────────────────────────────
-- Q10 · Eficiência Operacional — Cost-to-Income por Marca
-- ────────────────────────────────────────────────────────────
SELECT
    m.nome                                  AS marca,
    k.ano,
    SUM(k.receita)                         AS receita_total,
    SUM(k.custos)                          AS custos_totais,
    SUM(k.lucro_bruto)                     AS lucro_bruto,
    ROUND(SUM(k.custos)/SUM(k.receita)*100, 1)  AS cost_to_income_pct,
    ROUND(SUM(k.lucro_bruto)/SUM(k.receita)*100, 1) AS margem_lucro_pct
FROM fact_kpis_mensais k
JOIN dim_marcas m ON k.marca_id = m.marca_id
GROUP BY m.nome, k.ano
ORDER BY k.ano, cost_to_income_pct;

-- ────────────────────────────────────────────────────────────
-- Q11 · Distribuição de Receita por Tipo de Produto (Mix)
-- ────────────────────────────────────────────────────────────
WITH total AS (SELECT SUM(receita) AS total FROM fact_transacoes)
SELECT
    p.tipo,
    COUNT(t.transacao_id)                   AS num_transacoes,
    ROUND(SUM(t.receita), 2)               AS receita,
    ROUND(SUM(t.receita) / total.total * 100, 1) AS quota_pct
FROM fact_transacoes t
JOIN dim_produtos p ON t.produto_id = p.produto_id
CROSS JOIN total
GROUP BY p.tipo, total.total
ORDER BY receita DESC;

-- ────────────────────────────────────────────────────────────
-- Q12 · Comparativo Mensal 2023 vs 2024
-- ────────────────────────────────────────────────────────────
SELECT
    k23.mes,
    m.nome                                              AS marca,
    k23.receita                                         AS receita_2023,
    k24.receita                                         AS receita_2024,
    ROUND(k24.receita - k23.receita, 2)                AS variacao_abs,
    ROUND((k24.receita - k23.receita)/k23.receita*100, 1) AS variacao_pct
FROM fact_kpis_mensais k23
JOIN fact_kpis_mensais k24 ON k23.marca_id = k24.marca_id AND k23.mes = k24.mes
    AND k23.ano = 2023 AND k24.ano = 2024
JOIN dim_marcas m ON k23.marca_id = m.marca_id
ORDER BY k23.mes, m.nome;

-- ────────────────────────────────────────────────────────────
-- Q13 · AUM (Assets Under Management) — Investimentos
-- ────────────────────────────────────────────────────────────
SELECT
    k.periodo,
    k.aum                   AS aum_mes,
    SUM(k.aum) OVER (
        PARTITION BY k.ano
        ORDER BY k.mes
    )                       AS aum_ytd,
    ROUND(k.receita / NULLIF(k.aum, 0) * 100, 2) AS yield_pct
FROM fact_kpis_mensais k
WHERE k.marca_id = 3
ORDER BY k.ano, k.mes;

-- ────────────────────────────────────────────────────────────
-- Q14 · Novos Clientes por Mês (Cohort de Adesão)
-- ────────────────────────────────────────────────────────────
SELECT
    DATE_FORMAT(data_adesao, '%Y-%m') AS mes_adesao,
    marca_id,
    segmento,
    COUNT(*)                           AS novos_clientes
FROM dim_clientes
GROUP BY mes_adesao, marca_id, segmento
ORDER BY mes_adesao, marca_id;

-- ────────────────────────────────────────────────────────────
-- Q15 · Ranking de Produtos Dentro de Cada Marca
-- ────────────────────────────────────────────────────────────
SELECT
    m.nome                              AS marca,
    p.nome                              AS produto,
    p.tipo,
    ROUND(SUM(t.receita), 2)           AS receita,
    RANK() OVER (
        PARTITION BY t.marca_id
        ORDER BY SUM(t.receita) DESC
    )                                   AS ranking_na_marca
FROM fact_transacoes t
JOIN dim_produtos p ON t.produto_id = p.produto_id
JOIN dim_marcas m ON t.marca_id = m.marca_id
GROUP BY m.nome, p.nome, p.tipo, t.marca_id
ORDER BY m.nome, ranking_na_marca;

-- ────────────────────────────────────────────────────────────
-- Q16 · EBITDA Estimado do Grupo por Ano
-- ────────────────────────────────────────────────────────────
SELECT
    ano,
    ROUND(SUM(receita), 2)                          AS receita_grupo,
    ROUND(SUM(custos), 2)                           AS custos_operacionais,
    ROUND(SUM(lucro_bruto), 2)                     AS ebitda_estimado,
    ROUND(SUM(lucro_bruto)/SUM(receita)*100, 1)    AS margem_ebitda_pct,
    SUM(num_transacoes)                             AS total_transacoes,
    SUM(clientes_ativos)                            AS total_clientes_ativos
FROM fact_kpis_mensais
GROUP BY ano
ORDER BY ano;

-- ────────────────────────────────────────────────────────────
-- Q17 · Concentração de Clientes (Índice de Herfindahl)
-- ────────────────────────────────────────────────────────────
WITH receita_cliente AS (
    SELECT cliente_id, SUM(receita) AS receita_total
    FROM fact_transacoes GROUP BY cliente_id
),
total AS (SELECT SUM(receita) AS grand_total FROM fact_transacoes)
SELECT
    rc.cliente_id,
    c.nome,
    rc.receita_total,
    ROUND(rc.receita_total / t.grand_total * 100, 2) AS quota_pct,
    ROUND(POWER(rc.receita_total / t.grand_total * 100, 2), 4) AS contributo_hhi
FROM receita_cliente rc
JOIN dim_clientes c ON rc.cliente_id = c.cliente_id
CROSS JOIN total t
ORDER BY rc.receita_total DESC;

-- ────────────────────────────────────────────────────────────
-- Q18 · Resumo Executivo Trimestral (Dashboard View)
-- ────────────────────────────────────────────────────────────
SELECT
    k.ano,
    CONCAT('Q', CEIL(k.mes/3.0)) AS trimestre,
    m.nome                        AS marca,
    SUM(k.receita)               AS receita,
    SUM(k.lucro_bruto)           AS lucro,
    ROUND(AVG(k.margem_pct), 1) AS margem_pct,
    SUM(k.clientes_ativos)       AS clientes,
    SUM(k.num_transacoes)        AS transacoes
FROM fact_kpis_mensais k
JOIN dim_marcas m ON k.marca_id = m.marca_id
GROUP BY k.ano, CEIL(k.mes/3.0), m.nome
ORDER BY k.ano, CEIL(k.mes/3.0), m.nome;

-- ────────────────────────────────────────────────────────────
-- Q19 · Ticket Médio por Segmento e Produto
-- ────────────────────────────────────────────────────────────
SELECT
    t.segmento,
    p.tipo,
    COUNT(*)                    AS contratos,
    ROUND(AVG(t.valor_contrato), 2) AS ticket_medio_contrato,
    ROUND(AVG(t.receita), 2)        AS receita_media,
    ROUND(MIN(t.receita), 2)        AS receita_min,
    ROUND(MAX(t.receita), 2)        AS receita_max
FROM fact_transacoes t
JOIN dim_produtos p ON t.produto_id = p.produto_id
GROUP BY t.segmento, p.tipo
ORDER BY t.segmento, receita_media DESC;

-- ────────────────────────────────────────────────────────────
-- Q20 · Vista Consolidada do Grupo (KPI Summary 2024)
-- ────────────────────────────────────────────────────────────
SELECT
    'AurumCap Grupo'             AS entidade,
    2024                        AS ano,
    ROUND(SUM(receita), 0)      AS receita_total_eur,
    ROUND(SUM(custos), 0)       AS custos_totais_eur,
    ROUND(SUM(lucro_bruto), 0)  AS ebitda_eur,
    ROUND(AVG(margem_pct), 1)   AS margem_media_pct,
    SUM(num_transacoes)         AS total_transacoes,
    SUM(clientes_ativos)        AS clientes_ativos_total,
    ROUND(SUM(aum), 0)          AS aum_total_eur
FROM fact_kpis_mensais
WHERE ano = 2024;
