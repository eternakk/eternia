# Eternia Infrastructure as Code
# Monitoring Module

# Variables for the module
variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
}

variable "prometheus_port" {
  description = "The port for Prometheus"
  type        = number
  default     = 9090
}

variable "alertmanager_port" {
  description = "The port for Alertmanager"
  type        = number
  default     = 9093
}

variable "grafana_port" {
  description = "The port for Grafana"
  type        = number
  default     = 3000
}

variable "node_exporter_port" {
  description = "The port for Node Exporter"
  type        = number
  default     = 9100
}

variable "cadvisor_port" {
  description = "The port for cAdvisor"
  type        = number
  default     = 8080
}

# Docker network for monitoring
resource "docker_network" "monitoring_network" {
  name = "monitoring-network-${var.environment}"
}

# Prometheus container
resource "docker_container" "prometheus" {
  name  = "prometheus-${var.environment}"
  image = docker_image.prometheus.image_id
  
  ports {
    internal = 9090
    external = var.prometheus_port
  }
  
  volumes {
    container_path = "/etc/prometheus"
    host_path      = "/path/to/prometheus/config"  # This should be updated to the actual path
    read_only      = true
  }
  
  volumes {
    container_path = "/prometheus"
    host_path      = "/path/to/prometheus/data"  # This should be updated to the actual path
  }
  
  networks_advanced {
    name = docker_network.monitoring_network.name
  }
  
  restart = "unless-stopped"
}

# Alertmanager container
resource "docker_container" "alertmanager" {
  name  = "alertmanager-${var.environment}"
  image = docker_image.alertmanager.image_id
  
  ports {
    internal = 9093
    external = var.alertmanager_port
  }
  
  volumes {
    container_path = "/etc/alertmanager"
    host_path      = "/path/to/alertmanager/config"  # This should be updated to the actual path
    read_only      = true
  }
  
  networks_advanced {
    name = docker_network.monitoring_network.name
  }
  
  restart = "unless-stopped"
}

# Grafana container
resource "docker_container" "grafana" {
  name  = "grafana-${var.environment}"
  image = docker_image.grafana.image_id
  
  ports {
    internal = 3000
    external = var.grafana_port
  }
  
  volumes {
    container_path = "/etc/grafana"
    host_path      = "/path/to/grafana/config"  # This should be updated to the actual path
    read_only      = true
  }
  
  volumes {
    container_path = "/var/lib/grafana"
    host_path      = "/path/to/grafana/data"  # This should be updated to the actual path
  }
  
  networks_advanced {
    name = docker_network.monitoring_network.name
  }
  
  restart = "unless-stopped"
}

# Node Exporter container
resource "docker_container" "node_exporter" {
  name  = "node-exporter-${var.environment}"
  image = docker_image.node_exporter.image_id
  
  ports {
    internal = 9100
    external = var.node_exporter_port
  }
  
  volumes {
    container_path = "/host/proc"
    host_path      = "/proc"
    read_only      = true
  }
  
  volumes {
    container_path = "/host/sys"
    host_path      = "/sys"
    read_only      = true
  }
  
  volumes {
    container_path = "/rootfs"
    host_path      = "/"
    read_only      = true
  }
  
  networks_advanced {
    name = docker_network.monitoring_network.name
  }
  
  restart = "unless-stopped"
  
  command = [
    "--path.procfs=/host/proc",
    "--path.sysfs=/host/sys",
    "--path.rootfs=/rootfs"
  ]
}

# cAdvisor container
resource "docker_container" "cadvisor" {
  name  = "cadvisor-${var.environment}"
  image = docker_image.cadvisor.image_id
  
  ports {
    internal = 8080
    external = var.cadvisor_port
  }
  
  volumes {
    container_path = "/var/run"
    host_path      = "/var/run"
    read_only      = true
  }
  
  volumes {
    container_path = "/sys"
    host_path      = "/sys"
    read_only      = true
  }
  
  volumes {
    container_path = "/var/lib/docker"
    host_path      = "/var/lib/docker"
    read_only      = true
  }
  
  networks_advanced {
    name = docker_network.monitoring_network.name
  }
  
  restart = "unless-stopped"
}

# Docker images
resource "docker_image" "prometheus" {
  name = "prom/prometheus:latest"
}

resource "docker_image" "alertmanager" {
  name = "prom/alertmanager:latest"
}

resource "docker_image" "grafana" {
  name = "grafana/grafana:latest"
}

resource "docker_image" "node_exporter" {
  name = "prom/node-exporter:latest"
}

resource "docker_image" "cadvisor" {
  name = "gcr.io/cadvisor/cadvisor:latest"
}

# Outputs
output "prometheus_url" {
  description = "The URL for Prometheus"
  value       = "http://localhost:${var.prometheus_port}"
}

output "alertmanager_url" {
  description = "The URL for Alertmanager"
  value       = "http://localhost:${var.alertmanager_port}"
}

output "grafana_url" {
  description = "The URL for Grafana"
  value       = "http://localhost:${var.grafana_port}"
}