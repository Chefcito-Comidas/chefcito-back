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

### Repositorios

El repositorio del sistema se encontrara alojado en [github](github.com), utilizando la herramienta
*git* y contando el mismo con la siguiente estructura de carpetas:

- src
    - services
        - Contiene un modulo por servicio construido que implementan la interfaz del mismo.
    - model
        - Contiene modulos y archivos de codigo que implementan la logica de cada uno de los servicios. Que se implementan
        utilizando la siguiente estructura de modulos
            - model
                - Contiene la logica de negocio del servicio
            - interfaces
                - Contiene la implementacion de interfaces que el servicio necesita utilizar como pueden ser
                Bases de Datos, APIs externas al servicio, etc.
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

## Diagrama general del sistema

Diagramar utilizando Excalidraw de la forma mas sencilla posible el sistema desde
afuera. Voy a usar un patron de Gateway

## Metodologia de autenticacion de usuarios

Voy a ir por Firebase/Existe la posibilidad de usar Amplify

### Creacion de usuarios y storage de contraseñas

La idea es que use un servicio externo para hacer todas estas cosas, tanto identidad 
federada como identidad por usuario y contraseña

### Autenticacion por identidad federada

## Metodologia de autorizacion de usuarios

Aca tengo que tener una manera de poder obtener el rol que tiene el usuario, segun como
se haya registrado o incluso si no esta registrado.
