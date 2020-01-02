job "python-app-template" {
  datacenters = ["aws-${aws_region}"]
  type        = "service"

  meta {
    lang = "python"
    proj = "python-app-template"
  }

  group "pythonapptemplate" {
    count = "${count}"

    meta {
      group = "pythonapptemplate"
    }

    restart {
      attempts = 10
      interval = "5m"
      delay    = "25s"
      mode     = "delay"
    }

    task "run-python-app-template" {
      driver = "docker"

      env {
        env_path = "$${NOMAD_META_proj}/env"
        app      = "python-app-template"
        command  = "run-python-app-template"
      }

      config {
        image      = "${ecr_url}/zf/${app}:${git_rev}"
        force_pull = true

        volumes = [
          "env:/local/env",
        ]

        port_map {
          http = 80
        }

        cpu_hard_limit = true
      }

      resources {
        cpu    = "${cpu_mhz}" # 2999 MHz is 1 c5.2xl CPU
        memory = 1500 # 1.5GB

        network {
          mbits = 1
          port  "http"{}
        }
      }

      service {
        name = "$${NOMAD_META_proj}"
        tags = []
        port = "http"

        check {
          name     = "python-app-template run-python-app-template command http Health Check"
          type     = "http"
          protocol = "https"
          path     = "/health"
          interval = "5s"
          timeout  = "2s"
          port     = "http"
        }
      }

      vault {
        policies    = ["python-app-template"]
        change_mode = "restart"
      }

      template {
        destination = "$${NOMAD_SECRETS_DIR}/server.bundle.pem"

        data = <<EOH
{{ $private_ip := env "NOMAD_IP_http" }}
{{ $ip_sans := printf "ip_sans=%s" $private_ip }}
{{ with secret "pki/ica/issue/python-app-template" "common_name=python-app-template.service.consul" "alt_names=python-app-template.service.aws-${aws_region}.consul" $ip_sans "format=pem" }}
{{ .Data.certificate }}
{{ .Data.issuing_ca }}
{{ .Data.private_key }}{{ end }}
EOH
      }

      template {
        data = <<EOH
{{ range ls "python-app-template/run-python-app-template/env" }}
{{ .Key|toUpper }}="{{ .Value }}"{{ end }}
EOH

        destination = "env"
        env         = true
        change_mode = "restart"
      }

      template {
        source      = "/nomad/templates/vault.crt.ctmpl"
        destination = "$${NOMAD_TASK_DIR}/vault.crt"
        change_mode = "restart"
      }
    }

    task "filebeat" {
      driver = "docker"

      # These variables are used to define this filebeats configuration
      env {
        # This is the name of this filebeat service.
        # It should be in the format of <meta.proj><meta.group>.filebeat
        common_name = "python-app-template.server.filebeat"

        # This is the index in elasticsearch that these logs should go to.
        # This should generally be the project's name.
        index_name = "python-app-template"

        # This is the task name that is having it's logs shipped.
        # It should be the other task in this group.
        task_log = "server"
      }

      config {
        image      = "${ecr_url}/zf/filebeat:master"
        force_pull = true
      }

      resources {
        cpu    = 100 # 100 MHz
        memory = 32  # 32MB

        network {
          mbits = 1
        }
      }

      service {
        name = "$${NOMAD_TASK_NAME}"
        tags = ["$${NOMAD_META_proj}.$${NOMAD_META_group}"]

        check {
          name     = "Filebeat check"
          type     = "script"
          command  = "pidof"
          args     = ["filebeat"]
          interval = "10s"
          timeout  = "2s"
        }
      }

      vault {
        policies    = ["filebeat"]
        change_mode = "restart"
      }

      template {
        source      = "/nomad/templates/client.bundle.pem.ctmpl"
        destination = "$${NOMAD_SECRETS_DIR}/client.bundle.pem"
        change_mode = "restart"
      }

      template {
        source      = "/nomad/templates/vault.crt.ctmpl"
        destination = "$${NOMAD_TASK_DIR}/vault.crt"
        change_mode = "restart"
      }
    }
  }
}