variable "project_id" {
  description = "ID do projeto no GCP"
  type        = string
}

variable "location" {
  description = "Localização dos recursos"
  type        = string
}

variable "region" {
  description = "Região dos recursos"
  type        = string
}

variable "image_version" {
  description = "Versão da imagem do Cloud Composer"
  type        = string
}

variable "environment_size" {
  description = "Tamanho do ambiente do Composer"
  type        = string
}

variable "repository_id" {
  type    = string
  default = "selenium-images"
}

variable "zone" {
  description = "Zona GCP"
  type        = string
  default     = "us-central1-a"
}
variable "project_number" {
  description = "Número do projeto GCP (não o project_id)"
  type        = string
    default     = "123456789012"  
}

variable "composer_sa" {
  description = "Service Account do Cloud Composer (Airflow)"
  default     = "composer-sa@lobobranco-458901.iam.gserviceaccount.com"
}