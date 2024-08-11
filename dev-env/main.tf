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
  env = ["DEV=True"]
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}


resource "docker_container" "users" {
  name = "users"
  hostname = "users"
  image = "service-users:latest"
  env = ["API_KEY=superSecret", "DB_STRING=postgresql://user:admin123@reldb/users_db"]
  ports {
    internal = 80
    external = 8001
  }
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}


resource "docker_container" "venues" {
  name = "venues"
  hostname = "venues"
  image = "service-venues:latest"
  ports {
    internal = 80
    external = 8003
  }
  env=["DB_STRING=postgresql://user:admin123@reldb/users_db"]
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

resource "docker_container" "reservations" {
  name = "reservations"
  hostname = "reservations"
  image = "service-reservations:latest"
  ports {
    internal = 80
    external = 8002
  }
  env=["DB_STRING=postgresql://user:admin123@reldb/users_db"]
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

resource "docker_container" "opinions" {
  name = "opinions"
  hostname = "opinions"
  image = "service-opinions:latest"
  ports {
    internal = 80
    external = 8004
  }
  env = ["CONN_STRING=mongodb://nsqldb/"]
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

resource "docker_container" "summaries" {
  name = "summaries"
  hostname = "summaries"
  image = "service-summaries:latest"
  ports {
    internal = 80
    external = 8005
  }
  env = ["CONN_STRING=mongodb://nsqldb/", "KEY=FakeKey", "KEY_ID=FAKEKEYID"]
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

resource "docker_container" "postgresql" {
  name = "postgredb"
  hostname = "reldb"
  image = "postgres:16.3"
  env = ["POSTGRES_USER=user", "POSTGRES_PASSWORD=admin123", "POSTGRES_DB=users_db"]
  ports {
    internal = 5432
    external = 5432
  }
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}

resource "docker_container" "mongo" {
  name = "mongodb"
  hostname = "nsqldb"
  image = "mongo:8.0-rc"
  ports {
    internal = 27017
    external = 27017
  }
  networks_advanced {
    name = docker_network.chefcito_network.id
  }
}
