variable "name" {}
variable "region" {}
variable "project_id" {}
variable "image_version" {
  description = "Versão da imagem do Composer"
  type        = string
}
variable "environment_size" {
  type        = string
}
