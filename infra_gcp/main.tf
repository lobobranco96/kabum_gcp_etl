#####################################################################
# Projeto de Infraestrutura GCP para Pipeline de Dados da Kabum
# Recursos provisionados:
# - Buckets GCS (raw e processed)
# - Dataset e tabela BigQuery
# - Cluster GKE leve para testes com K8sPodOperator
# - Repositório Docker no Artifact Registry
# - Environment do Cloud Composer com dependências Airflow
# - IAM para integrações seguras entre serviços
#####################################################################

#####################
# Módulo BigQuery
#####################


# Criação do dataset "kabum_dataset"
module "dataset" {
  source     = "./modules/bigquery_dataset"
  dataset_id = "kabum_dataset"
  location   = var.location
}

# Criação da tabela "produtos" com schema definido em JSON
module "produtos" {
  source     = "./modules/bigquery_table"
  dataset_id = module.dataset.dataset_id
  table_id   = "produtos"
  schema     = file("${path.module}/schemas/produtos_schema.json")
}

#####################
# Buckets GCS
#####################

# Bucket para dados brutos (raw)
module "raw_bucket" {
  source        = "./modules/storage_bucket"
  name          = "kabum-raw"
  location      = var.location
  force_destroy = true
}

# Bucket para dados transformados (processed)
module "processed_bucket" {
  source        = "./modules/storage_bucket"
  name          = "kabum-processed"
  location      = var.location
  force_destroy = true
}

#############################
# Artifact Registry + Build
#############################

# Repositório Docker para armazenar imagem do scraper Selenium
resource "google_artifact_registry_repository" "docker_repo" {
  provider      = google
  location      = var.region
  repository_id = var.repository_id
  description   = "Repositório Docker para imagens do Selenium"
  format        = "DOCKER"
}

# Envia a imagem Docker para o Artifact Registry usando o Cloud Build
resource "null_resource" "build_docker_image" {
  provisioner "local-exec" {
    command = "gcloud builds submit --project=${var.project_id} --tag=us-central1-docker.pkg.dev/${var.project_id}/selenium-images/scraper:latest ${path.module}/docker"
  }
}

#############################
# Cloud Composer
#############################

# Provisiona ambiente gerenciado do Airflow com dependências necessárias
module "composer_env" {
  source           = "./modules/composer"
  name             = "lobobranco-composer"
  region           = var.region     
  project_id       = var.project_id
  image_version    = var.image_version  
  environment_size = var.environment_size

  pypi_packages = {
    "apache-airflow-providers-cncf-kubernetes" = "==8.4.2"
    "kubernetes" = ">=29.0.0,<32.0.0"
  }
}

data "google_project" "project" {
  project_id = var.project_id
}


#############################
# IAM: Permissões de serviço
#############################

# Concede permissões ao Cloud Build e Cloud Composer para:
# - Gerenciar buckets
# - Acessar imagens Docker
# - Executar jobs BigQuery
# - Ler objetos no GCS

locals {
  cloudbuild_sa = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  compute_sa    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = local.cloudbuild_sa
}

resource "google_project_iam_member" "cloudbuild_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = local.cloudbuild_sa
}

resource "google_project_iam_member" "compute_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = local.compute_sa
}

resource "google_project_iam_member" "compute_composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = local.compute_sa
}


resource "google_project_iam_member" "composer_worker_container" {
  project = var.project_id
  role    = "roles/container.developer"
  member  = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "composer_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "composer_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${var.composer_sa}"
}

resource "google_project_iam_member" "composer_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${var.composer_sa}"
}

resource "google_project_iam_member" "composer_storage_object_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${var.composer_sa}"
}

# GKE usado para executar workloads via KubernetesPodOperator
resource "google_container_cluster" "primary" {
  name     = "cluster-airflow-leve"
  location = var.zone

  deletion_protection = false 

  initial_node_count = 1

  node_config {
    machine_type     = "e2-small"
    disk_size_gb     = 10
    local_ssd_count  = 0
    oauth_scopes     = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

data "google_client_config" "default" {}

# Acesso à API Kubernetes via Terraform
provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

# Concede ao Airflow permissão de editar recursos no namespace do Composer
resource "kubernetes_cluster_role_binding" "airflow_gke_access" {
  metadata {
    name = "airflow-gke-access"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "edit"
  }

  subject {
    kind      = "ServiceAccount"
    name      = "default"
    namespace = "composer-workloads"
  }
}
