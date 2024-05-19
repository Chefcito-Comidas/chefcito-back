terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "3.0.2"
    }  
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "chefcito_network" {
  name = "chefcito-system"
  ipam_config {
    subnet = "172.25.125.0/24"
  }
}

resource "docker_container" "gateway" {
  name = "gateway"
  hostname = "gateway"
  image = "service-gateway:latest"
  ports {
    internal = 80
    external = 8000
  }
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}


resource "docker_container" "users" {
  name = "users"
  hostname = "users"
  image = "service-users:latest"
  env = ["API_KEY=secretApiKey"]
  ports {
    internal = 80
    external = 8001
  }
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

