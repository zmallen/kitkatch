variable "app" {
  default = "python-app-template"
}

variable "env" {
  default = "qa"
}

variable "git_sha" {
  default = "master"
}

variable "aws_region" {}

variable "remote_state_s3_bucket_prefix" {}

variable "ecr_url" {}

variable "container_count" {
  type = "map"
}

variable "cpu_mhz_env" {
  type = "map"
}
