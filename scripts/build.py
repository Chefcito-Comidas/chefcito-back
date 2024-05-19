import docker
import os

CONTAINER_DIR = "containerfiles"
CONTAINER_FILE_NAME = "CONTAINERFILE"
PATH_SEPARATOR = '/'
SERVICE_PREFIX = "service"
SERVICE_SEPARATOR = '-'


if __name__ == "__main__":
    client = docker.from_env()
    for (root, dir_name, file_name) in os.walk(f"./{CONTAINER_DIR}"):
        #Remove start "./"
        root = root.lstrip("./\\")
        if file_name:
            container_path = os.path.join(".", root, CONTAINER_FILE_NAME)
            service_name = root.replace(CONTAINER_DIR, SERVICE_PREFIX).replace(PATH_SEPARATOR, SERVICE_SEPARATOR) 
            print(f"Building service ===> {service_name}\nAt ===> {container_path}")
            client.images.build(path='.',dockerfile=container_path, tag=service_name)
