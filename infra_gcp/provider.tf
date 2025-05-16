terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }

  required_version = ">= 1.0"
}

provider "google" {
  credentials = file("${path.module}/credencial/lobobranco-458901-2d6bc0756f93.json")
  project     = var.project_id
}