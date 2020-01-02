terraform {
  backend "s3" {
    key = "python-app-template/terraform.tfstate"
  }
}

provider "aws" {
  region = "${var.aws_region}"
}

provider "nomad" {
  address = "https://nomad-${var.env}.zerofox.com"
  region  = "global"
}

provider "consul" {
  address    = "consul-${var.env}.zerofox.com:443"
  datacenter = "aws-${var.aws_region}"
  scheme     = "https"
}

# ------------------------------------------------------------------------
# Nomad
# ------------------------------------------------------------------------
data "template_file" "nomad_job_spec" {
  template = "${file("python-app-template.nomad.hcl")}"

  vars {
    ecr_url    = "${var.ecr_url}"
    app        = "${var.app}"
    git_rev    = "${var.git_sha}"
    aws_region = "${var.aws_region}"

    count   = "${var.container_count[var.env]}"
    cpu_mhz = "${var.cpu_mhz_env[var.env]}"
  }
}

module "build_image_and_run_job" {
  source = "git::ssh://git@github.com/riskive/devops-terraform-modules.git?ref=master//components/nomad-build-run"

  ecr_url           = "${var.ecr_url}"
  app               = "${var.app}"
  git_sha           = "${var.git_sha}"
  rendered_template = "${data.template_file.nomad_job_spec.rendered}"
}

# ------------------------------------------------------------------------
# AWS
# ------------------------------------------------------------------------
resource "aws_iam_role" "iam_role" {
  name = "${var.env}-${var.app}-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "consul_keys" "pythonapptemplate_arn" {
  key {
    path  = "${var.app}/run-python-app-template/env/NUM_WORKERS"
    value = "3"
  }

  key {
    path  = "${var.app}/run-python-app-template/env/KEYFILE_PATH"
    value = "/secrets/server.bundle.pem"
  }

  key {
    path  = "${var.app}/run-python-app-template/env/CERTFILE_PATH"
    value = "/secrets/server.bundle.pem"
  }

  key {
    path  = "${var.app}/run-python-app-template/env/LOG_LEVEL"
    value = "info"
  }
}