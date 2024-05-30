# Back-end Chefcito 

## Tecnologias

El sistema se desarrolla utilizando Python (3.12) y FastAPI (0.111.0) como lenguaje 
de programacion principal y framework principal. En el caso de que se requiera construir
algun servicio para el cual no hay librerias o frameworks compatibles con estas versiones
se desarrollara tal servicio utilizando Golang (1.22).

### Herramientas de desarrollo

Los servicios del sistema seran contenerizados utilizando una solucion de contenederos que
sea compatible con el Standard OSI y los archivos de contenedores llevaran el nombre de
**CONTAINERFILE**.
Para la construccion de un entorno de desarrollo local se utilizara Docker-Compose o bien
alguna herramienta que permita crear un cluster de un unico nodo de Kubernetes. El sistema
productivo estara deployeado sobre Kubernetes y se utilizara Terraform como herramienta
de gestion de la infraestructura.

#### Chefcito-CLI

Chefcito cli es un programa de consola que facilita la tarea de desarrollo local del sistema en general. 

##### Instalacion

<Explicar como se instala chefcito cli>

##### Uso de chefcito

<Explicar los comandos de chefcito cli>

### Repositorios

El repositorio del sistema se encontrara alojado en [github](github.com), utilizando la herramienta
*git* y contando el mismo con la siguiente estructura de carpetas:

- src
    - services
        - Contiene un modulo por servicio construido que implementan al servicio integrado con la interfaz de FastAPI.
    - model
        - Contiene modulos y archivos de codigo que implementan la logica de cada uno de los servicios. Todo modelo de servicio tiene que contener
          un modulo service que implemente la interfaz del propio servicio.
- test
    - Contiene todas las pruebas unitarias de los servicios en *src*, utiliza la misma misma estructura de modulos que *src*
- containerfiles
    - Contiene todos los archivos de Contenedores del sistema, cada contenedor construye una imagen de un unico servicio del 
    sistema.
- README.MD
    - Contiene informacion importante del sistema, como puede ser la forma en la que esta construido, la utilizacion del mismo para levantar
    un ambiente local de desarrollo y la forma de ejecutar el sistema como un servicio en la nube.
- requirements.txt
    - Contiene todos los requerimientos de librerias del sistema.
- dev-requirements.txt
    - Contiene los requerimientos de librerias que no forman parte del sistema pero cumplen algun rol en el desarrollo del mismo.

### Dev Guidelines

Explicar la manera en la que se desarrolla chefcito.

## Diagrama general del sistema

Diagramar utilizando Excalidraw de la forma mas sencilla posible el sistema desde
afuera. Voy a usar un patron de Gateway.
