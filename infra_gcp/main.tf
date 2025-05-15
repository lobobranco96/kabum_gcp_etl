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

# Criação do ambiente Composer
module "composer_env" {
  source           = "./modules/composer"
  name             = "lobobranco-composer"
  region           = var.region     
  project_id       = var.project_id
  image_version    = var.image_version  
  environment_size = var.environment_size

  # imagem customizada com Selenium + Chrome
  docker_image_repository = "us-central1-docker.pkg.dev/${var.project_id}/selenium-images/scraper:latest"
}
