# Projeto de Infraestrutura com Terraform na Google Cloud

Este repositório demonstra minha experiência prática com **Terraform**, utilizando **Google Cloud Platform (GCP)** como provedor. O foco principal é a automação e provisionamento de recursos em nuvem para uma stack de engenharia de dados moderna.

---

## Tecnologias e Ferramentas

- **Terraform** (Infraestrutura como Código - IaC)
- **Google Cloud Platform** (GCP)
  - Cloud Storage
  - BigQuery
  - Cloud Composer
- **Módulos reutilizáveis** e organização limpa por componentes
- **Provisionamento automatizado** com variáveis e boas práticas de modularização

---

## Recursos Provisionados

### 1. **Buckets no Cloud Storage**
Provisionamento automático de buckets para diferentes camadas de um Data Lake:

- `lobobranco-raw` → Camada Raw
- `lobobranco-processed` → Camada Processada
- `lobobranco-compose` → DAGs e logs do Cloud Composer

---

### 2. **BigQuery**
Criação de:

- Dataset: `etl_dataset`
- Tabelas:
  - `clientes`
  - `vendas`
  
Schemas definidos em JSON para garantir consistência de dados.

---

### 3. **Cloud Composer (Airflow gerenciado)**
Criação de um ambiente do **Composer 3 (Airflow 2.9.3)** com:

- Tamanho configurável (`ENVIRONMENT_SIZE_SMALL`)
- Configuração de variáveis de ambiente
- Recursos de CPU/memória definidos para `scheduler`, `worker` e `web_server`
- Bucket próprio para armazenar DAGs

---

## Organização do Código

```bash
├── main.tf
├── variables.tf
├── provider.tf
├── terraform.tfvars
├── modules/
│ ├── bigquery_dataset/
│ ├── bigquery_table/
│ ├── storage_bucket/
│ └── composer/
├── schemas/
│ └── orodutos_schema.json
├── credencial/
│ └── chave.json
└── docs/
```
---
## Como usar

> Pré-requisitos: Terraform instalado e credencial do service-account do GCP baixada e armazenada no diretorio de credencial`

> In
```bash
!gcloud auth activate-service-account --key-file=/infra_gcp/credencial/lobobranco-458901-2d6bc0756f93.json

# Define o projeto corretamente
!gcloud config set project lobobranco-458901

# adicionar ao service account do compute engine as roles necessarias
!gcloud projects add-iam-policy-binding lobobranco-458901 \
   --member="serviceAccount:1075705997765@cloudbuild.gserviceaccount.com" \
   --role="roles/storage.admin"

# # Permissão para publicar imagens no Artifact Registry
!gcloud projects add-iam-policy-binding lobobranco-458901 \
   --member="serviceAccount:1075705997765@cloudbuild.gserviceaccount.com" \
   --role="roles/artifactregistry.writer"

# Dá permissão para acessar Cloud Storage
!gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:1075705997765-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"

# Dá permissão para o Cloud Composer funcionar
!gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:1075705997765-compute@developer.gserviceaccount.com" \
  --role="roles/composer.worker"
```


```bash
# Inicializar o Terraform
terraform init

# Visualizar o plano de execução
terraform plan

# Aplicar mudanças na infraestrutura
terraform apply --auto-approve

# Destruir toda a infra se necessario
terraform destroy --auto-approve
```

## Objetivo

Este repositório foi criado como uma demonstração prática de habilidades em Terraform, com foco em engenharia de dados em nuvem, evidenciando:

- Modularização
- Provisionamento escalável
- Boas práticas em IaC
- Integração com ferramentas modernas de dados