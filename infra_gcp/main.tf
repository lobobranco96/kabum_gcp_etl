module "dataset" {
  source     = "./modules/bigquery_dataset"
  dataset_id = "kabum_dataset"
  location   = var.location
}

module "produtos" {
  source     = "./modules/bigquery_table"
  dataset_id = module.dataset.dataset_id
  table_id   = "produtos"
  schema     = file("${path.module}/schemas/produtos_schema.json")
}

module "raw_bucket" {
  source        = "./modules/storage_bucket"
  name          = "kabum-raw"
  location      = var.location
  force_destroy = true
}

module "processed_bucket" {
  source        = "./modules/storage_bucket"
  name          = "kabum-processed"
  location      = var.location
  force_destroy = true
}

resource "google_artifact_registry_repository" "docker_repo" {
  provider      = google
  location      = var.region
  repository_id = var.repository_id
  description   = "Repositório Docker para imagens do Selenium"
  format        = "DOCKER"
}

resource "null_resource" "build_docker_image" {
  provisioner "local-exec" {
    command = "gcloud builds submit --project=${var.project_id} --tag=us-central1-docker.pkg.dev/${var.project_id}/selenium-images/scraper:latest ${path.module}/docker"
  }
}

module "composer_env" {
  source           = "./modules/composer"
  name             = "lobobranco-composer"
  region           = var.region     
  project_id       = var.project_id
  image_version    = var.image_version  
  environment_size = var.environment_size
  docker_image     = "us-central1-docker.pkg.dev/${var.project_id}/selenium-images/scraper:latest" 
}

resource "google_container_cluster" "primary" {
  name     = "cluster-airflow-leve"
  location = var.zone

  deletion_protection = false  # <-- isso aqui é o necessário

  initial_node_count = 1

  node_config {
    machine_type     = "e2-small"
    disk_size_gb     = 10
    local_ssd_count  = 0
    oauth_scopes     = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

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
    namespace = "default"
  }
}
