# Análise de Produtos Kabum - Queries Inteligentes

Este repositório contém queries SQL para análise dos dados de produtos coletados da Kabum, armazenados no BigQuery no dataset `kabum_dataset` e tabela `produtos`.

## Estrutura dos Dados

A tabela `produtos` possui as seguintes colunas principais:

| Coluna             | Tipo     | Descrição                            |
|--------------------|----------|------------------------------------|
| `nome_produto`     | STRING   | Nome do produto                    |
| `detalhes`         | STRING   | Descrição detalhada do produto     |
| `preco_atual`      | FLOAT    | Preço atual do produto             |
| `preco_antigo`     | FLOAT    | Preço antigo (antes do desconto)  |
| `desconto_percentual` | INTEGER | Percentual de desconto             |
| `avaliacao`        | INTEGER  | Avaliação do produto (número)      |
| `unidades`         | INTEGER  | Quantidade disponível em estoque   |
| `cupom`            | STRING   | Cupom aplicado, se houver          |
| `link`             | STRING   | URL para o produto no site         |

---
## Queries

### 1. Top 5 produtos com maior desconto absoluto (em R$)
```sql
SELECT 
  nome_produto,
  preco_antigo,
  preco_atual,
  ROUND(preco_antigo - preco_atual, 2) AS desconto_reais,
  desconto_percentual,
  link
FROM `lobobranco-458901.kabum_dataset.produtos`
ORDER BY desconto_reais DESC
LIMIT 5;
```

### 2. Top 5 produtos com maior desconto absoluto (em R$)
```sql
SELECT 
  nome_produto,
  preco_antigo,
  preco_atual,
  desconto_percentual,
  avaliacao,
  link
FROM `lobobranco-458901.kabum_dataset.produtos`
WHERE desconto_percentual > 40
  AND avaliacao >= 4
ORDER BY desconto_percentual DESC;
```

### 3. Produtos mais vendidos (com base em unidades)
```sql
SELECT 
  nome_produto,
  unidades,
  preco_atual,
  link
FROM `lobobranco-458901.kabum_dataset.produtos`
ORDER BY unidades DESC
LIMIT 5;
```

### 4. Produtos com cupom aplicado (e qual cupom foi usado)
```sql
SELECT 
  nome_produto,
  preco_atual,
  cupom,
  link
FROM `lobobranco-458901.kabum_dataset.produtos`
WHERE cupom IS NOT NULL AND cupom != ''
ORDER BY preco_atual DESC;
```

### 5. Distribuição dos descontos por cupom promocional
```sql
SELECT 
  cupom,
  COUNT(*) AS total_produtos,
  AVG(desconto_percentual) AS desconto_medio
FROM `lobobranco-458901.kabum_dataset.produtos`
WHERE cupom IS NOT NULL AND cupom != ''
GROUP BY cupom
ORDER BY desconto_medio DESC;
```

### 6. Produtos com maior quantidade disponível
```sql
SELECT 
  nome_produto,
  SUM(unidades) AS total_unidades
FROM `lobobranco-458901.kabum_dataset.produtos`
GROUP BY nome_produto
ORDER BY total_unidades DESC;
```

