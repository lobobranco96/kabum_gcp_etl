resource "google_composer_environment" "this" {
  name    = var.name
  region  = var.region
  project = var.project_id

  config {
    software_config {
      image_version = var.image_version

      # pacotes do requirements
      pypi_packages = var.pypi_packages
    }
      env_variables = {
        GOOGLE_PROJECT = var.project_id
        DOCKER_IMAGE   = var.docker_image
      }
    airflow_config_overrides = {
            "variables" = jsonencode({
              project_id = var.project_id
              processed_bucket = var.processed_bucket
              dataset     = var.dataset
              tabela      = var.tabela
            })
    }

    workloads_config {
      scheduler {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
      }
      web_server {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
      }
      worker {
        cpu        = 1
        memory_gb  = 2
        storage_gb = 1
      }
    }

    environment_size = var.environment_size
  }
}
