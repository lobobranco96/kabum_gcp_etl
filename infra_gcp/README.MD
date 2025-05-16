# Projeto de Infraestrutura com Terraform na Google Cloud

Este repositório demonstra minha experiência prática com **Terraform**, utilizando **Google Cloud Platform (GCP)** como provedor. O foco principal é a automação e provisionamento de recursos em nuvem para uma stack de engenharia de dados moderna, com infraestrutura para orquestração via Airflow e processamento via GKE.

---

## Tecnologias e Ferramentas

- **Terraform** (Infraestrutura como Código - IaC)
- **Google Cloud Platform** (GCP)
  - Cloud Storage
  - BigQuery
  - Artifact Registry (Repositório Docker)
  - Cloud Composer (Airflow gerenciado)
  - Google Kubernetes Engine (GKE)
- **gcloud CLI**
- **Módulos reutilizáveis** e organização limpa por componentes
- **Provisionamento automatizado** com variáveis e boas práticas de modularização
- **Configuração Kubernetes Provider** para integração com cluster GKE criado

---

## Recursos Provisionados

### 1. **Buckets no Cloud Storage**

Provisionamento automático de buckets para diferentes camadas de um Data Lake:

- `kabum-raw` → Camada Raw  
- `kabum-processed` → Camada Processada

### 2. **BigQuery**

Criação de:

- Dataset: `kabum_dataset`  
- Tabelas:
  - `produtos`

Schemas definidos em JSON para garantir consistência de dados.

### 3. **Artifact Registry**

- Repositório Docker para armazenar imagens de containers, especialmente imagens customizadas do Selenium usadas nas pipelines.

### 4. **Docker Image Build**

- Build e push automatizado de imagem Docker para o Artifact Registry via provisioner `local-exec` rodando comando `gcloud builds submit`.

### 5. **Cloud Composer (Airflow gerenciado)**

Criação de um ambiente do **Composer 3 (Airflow 2.9.3)** com:

- Tamanho configurável (exemplo: `ENVIRONMENT_SIZE_SMALL`)  
- Configuração de variáveis de ambiente e recursos  
- Integração com buckets Cloud Storage para DAGs e requirements

### 6. **Google Kubernetes Engine (GKE)**

- Cluster Kubernetes chamado `cluster-airflow-leve` criado para execução de workloads relacionados ao Airflow/Composer.  
- Configuração de node pool básica (`e2-small`, 1 nó, 10GB disk).  
- Sem proteção de deleção para facilitar destruição e recriação.  
- Provider Kubernetes configurado automaticamente para se conectar ao cluster criado.

### 7. **Kubernetes RBAC**

- `ClusterRoleBinding` que concede permissão ao ServiceAccount `default` do namespace `composer-workloads` para modificar recursos no cluster (permite integração entre Airflow e GKE).

### 8. **Permissões IAM Automatizadas**

Automatização via Terraform das permissões necessárias para as Service Accounts do projeto:

- **Cloud Build Service Account**  
  - `roles/storage.admin` (acesso buckets Storage)  
  - `roles/artifactregistry.writer` (push de imagens Docker)  

- **Compute Engine Service Account**  
  - `roles/storage.admin` (acesso buckets Storage)  
  - `roles/composer.worker` (execução do Composer)  

- **Cloud Composer Service Account**  
  - `roles/container.developer` (acesso e modificação do cluster GKE)  
  - `roles/artifactregistry.reader` (leitura de imagens no Artifact Registry)

---

## Organização do Código

```bash
├── main.tf                    # Arquivo principal com recursos e módulos
├── variables.tf               # Declaração das variáveis usadas
├── provider.tf                # Configuração dos providers (Google, Kubernetes)
├── terraform.tfvars           # Valores para as variáveis (exemplo)
├── modules/                   # Módulos reutilizáveis (BigQuery, Buckets, Composer)
│   ├── bigquery_dataset/
│   ├── bigquery_table/
│   ├── storage_bucket/
│   └── composer/
├── schemas/                   # Schemas JSON para tabelas BigQuery
│   └── produtos_schema.json
└── credencial/                # Credenciais para autenticação GCP
    └── chave.json

```
---
## Como usar
# Pré-requisitos

- Terraform instalado
- gcloud CLI instalado
- Service Account do GCP com permissões para criar recursos
- Chave JSON da service account armazenada localmente (/infra_gcp/credencial/chave.json)
- Autenticação e Permissões Manuais (somente se não automatizado)
- Para garantir que as service accounts tenham as permissões necessárias para execução, você pode executar os comandos abaixo localmente (ou automatizar via Terraform — veja o código do projeto):

É importante ter o cli da gcloud instalado https://cloud.google.com/sdk/docs/install?hl=pt-br para executar:
```bash
gcloud auth activate-service-account --key-file=/infra_gcp/credencial/lobobranco-458901-2d6bc0756f93.json
gcloud config set project lobobranco-458901
```

## Cloud Build permissions
```bash
gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:<PROJECT_NUMBER>@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```
## Compute Engine permissions
```bash
gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding lobobranco-458901 \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/composer.worker"
```
---

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
---
```bash
gsutil cp kabum_dag.py gs://<bucket_composer>/dags/
```

## Objetivo
Este repositório foi criado como uma demonstração prática de habilidades em Terraform, com foco em engenharia de dados em nuvem, evidenciando:

- Modularização e reutilização de código

- Provisionamento escalável e seguro

- Automação de permissões IAM

- Integração entre serviços GCP (Storage, BigQuery, Composer, GKE, Artifact Registry)

- Boas práticas em Infraestrutura como Código (IaC)