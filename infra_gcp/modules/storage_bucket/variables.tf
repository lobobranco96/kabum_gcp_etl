variable "name" {
  type = string
}

variable "location" {
  type    = string
  default = "US"
}

variable "force_destroy" {
  type    = bool
  default = true
}
