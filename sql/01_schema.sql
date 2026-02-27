-- ============================================================
-- NOVACAP GRUPO FINANCEIRO — Base de Dados
-- Projeto: Análise de Dados | Portfolio
-- Versão: 1.0 | Janeiro 2025
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. TABELAS DE DIMENSÃO
-- ────────────────────────────────────────────────────────────

CREATE TABLE dim_marcas (
    marca_id     INT          PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    setor        VARCHAR(100) NOT NULL,
    fundacao     INT,
    descricao    TEXT,
    ativo        BOOLEAN      DEFAULT TRUE,
    criado_em    DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_segmentos (
    segmento_id  INT          PRIMARY KEY AUTO_INCREMENT,
    nome         VARCHAR(50)  NOT NULL UNIQUE,
    descricao    TEXT,
    limite_min   DECIMAL(15,2),
    limite_max   DECIMAL(15,2)
);

CREATE TABLE dim_cidades (
    cidade_id    INT          PRIMARY KEY AUTO_INCREMENT,
    nome         VARCHAR(100) NOT NULL,
    regiao       VARCHAR(50),
    pais         VARCHAR(50)  DEFAULT 'Portugal'
);

CREATE TABLE dim_clientes (
    cliente_id   VARCHAR(10)  PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    cidade_id    INT,
    segmento     VARCHAR(50),
    marca_id     INT          NOT NULL,
    data_adesao  DATE,
    ativo        BOOLEAN      DEFAULT TRUE,
    criado_em    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (marca_id)   REFERENCES dim_marcas(marca_id),
    FOREIGN KEY (cidade_id)  REFERENCES dim_cidades(cidade_id)
);

CREATE TABLE dim_produtos (
    produto_id   VARCHAR(10)  PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    marca_id     INT          NOT NULL,
    tipo         VARCHAR(50)  NOT NULL,
    margem_pct   DECIMAL(5,2) NOT NULL,
    descricao    TEXT,
    ativo        BOOLEAN      DEFAULT TRUE,
    FOREIGN KEY (marca_id)   REFERENCES dim_marcas(marca_id)
);

CREATE TABLE dim_calendario (
    data_key     DATE         PRIMARY KEY,
    ano          INT          NOT NULL,
    trimestre    INT          NOT NULL,
    mes          INT          NOT NULL,
    nome_mes     VARCHAR(20)  NOT NULL,
    semana       INT,
    dia_semana   INT,
    e_fim_semana BOOLEAN,
    e_feriado    BOOLEAN      DEFAULT FALSE
);

-- ────────────────────────────────────────────────────────────
-- 2. TABELA DE FACTOS
-- ────────────────────────────────────────────────────────────

CREATE TABLE fact_transacoes (
    transacao_id    VARCHAR(10)  PRIMARY KEY,
    data_key        DATE         NOT NULL,
    cliente_id      VARCHAR(10)  NOT NULL,
    marca_id        INT          NOT NULL,
    produto_id      VARCHAR(10)  NOT NULL,
    valor_contrato  DECIMAL(15,2) NOT NULL,
    receita         DECIMAL(12,2) NOT NULL,
    cidade          VARCHAR(100),
    segmento        VARCHAR(50),
    criado_em       DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (data_key)    REFERENCES dim_calendario(data_key),
    FOREIGN KEY (cliente_id)  REFERENCES dim_clientes(cliente_id),
    FOREIGN KEY (marca_id)    REFERENCES dim_marcas(marca_id),
    FOREIGN KEY (produto_id)  REFERENCES dim_produtos(produto_id),
    INDEX idx_data     (data_key),
    INDEX idx_marca    (marca_id),
    INDEX idx_produto  (produto_id),
    INDEX idx_segmento (segmento)
);

CREATE TABLE fact_kpis_mensais (
    kpi_id          INT          PRIMARY KEY AUTO_INCREMENT,
    ano             INT          NOT NULL,
    mes             INT          NOT NULL,
    periodo         VARCHAR(10)  NOT NULL,
    marca_id        INT          NOT NULL,
    receita         DECIMAL(15,2) NOT NULL,
    custos          DECIMAL(15,2) NOT NULL,
    lucro_bruto     DECIMAL(15,2) NOT NULL,
    margem_pct      DECIMAL(5,1),
    num_transacoes  INT,
    clientes_ativos INT,
    aum             DECIMAL(18,2),
    FOREIGN KEY (marca_id) REFERENCES dim_marcas(marca_id),
    INDEX idx_periodo (periodo),
    INDEX idx_marca_periodo (marca_id, periodo)
);

-- ────────────────────────────────────────────────────────────
-- 3. SEED DATA — MARCAS E SEGMENTOS
-- ────────────────────────────────────────────────────────────

INSERT INTO dim_marcas VALUES
(1, 'AurumCap Banca',         'Banca de Retalho',  2001, 'Divisão de banca comercial e retalho do grupo', TRUE, NOW()),
(2, 'AurumCap Seguros',       'Seguros',            2005, 'Divisão de seguros vida, auto e habitação',     TRUE, NOW()),
(3, 'AurumCap Investimentos', 'Gestão de Ativos',   2010, 'Divisão de fundos e gestão de carteiras',       TRUE, NOW());

INSERT INTO dim_segmentos VALUES
(1, 'Particular',      'Clientes individuais - segmento base',             0,        50000),
(2, 'PME',             'Pequenas e médias empresas',                   50001,      500000),
(3, 'Corporate',       'Grandes empresas e grupos empresariais',       500001,  5000000),
(4, 'Private Banking', 'Clientes de elevado património (HNWI)',       5000001, 999999999);

INSERT INTO dim_cidades VALUES
(1,'Lisboa','Lisboa','Portugal'),  (2,'Porto','Norte','Portugal'),
(3,'Braga','Norte','Portugal'),    (4,'Coimbra','Centro','Portugal'),
(5,'Aveiro','Centro','Portugal'),  (6,'Faro','Algarve','Portugal'),
(7,'Setubal','Setubal','Portugal'),(8,'Leiria','Centro','Portugal'),
(9,'Viseu','Centro','Portugal'),   (10,'Evora','Alentejo','Portugal');
