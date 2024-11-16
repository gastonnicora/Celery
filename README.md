# Índice
1. [Introducción](#celery-para-tareas-asíncronas)
2. [Requisitos](#requisitos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Detener los Contenedores](#detener-los-contenedores)
6. [Tareas en Celery](#tareas)
7. [Licencia](#licencia)
8. [Contacto](#contacto)

## Celery para Tareas Asíncronas
Este proyecto contiene un servidor Celery configurado para gestionar tareas asíncronas. 
Celery se conecta con la API a través de Redis para obtener las tareas y, 
cuando llega el momento adecuado, realiza una solicitud HTTP a la API para ejecutar esas tareas.

## Requisitos

Este proyecto se ejecuta utilizando Docker y depende de los siguientes servicios:

- **api**: El servidor principal que maneja la lógica de la aplicación.
- **socket**: Para manejar la comunicación en tiempo real (WebSockets).
- **db**: Contenedor de base de datos (por ejemplo, PostgreSQL o MySQL).
- **redis**: Usado para la gestión de tareas asíncronas con Celery y almacenamiento en caché.
- **celery**: Procesamiento de tareas en segundo plano.
- **web**: La interfaz de usuario para interactuar con la aplicación a través de una página web.

## Tecnologías
- **Celery**: Framework para la ejecución de tareas asíncronas.
- **Redis**: Servidor de mensajería para Celery y comunicación con API.
- **Docker**: Para guardar en contenedores los servicios.

## Estructura del Proyecto
```bash
/python
│
├── app/
│   ├── __init__.py        
│   ├── celery.py           # Configuración de Celery y definición de tareas
│   ├── mediador.py         # Media entre los mensajes de redis y las tareas de Celery
│   └── redis.py            # Conexión  con redis y escucha de mensajes
├── Dockerfile              # Archivo Docker para construir el contenedor de Celery.
├── docker-compose.yml      # Configuración de Docker Compose para levantar los servicios.
├── requirements.txt        # Dependencias de Python.
├── run.py                  # Archivo de ejecución
└── version.txt             # Versión de la imagen.
```
## Instalación y Configuración

1. **Crear docker-compose**:
    Cree un archivo llamado ``docker-compose.yml`` que contenga:
    ```yaml
    version: '3.3'

    services:
      db:
        image: gastonnicora/remates-sql
        expose:
          - "3306"
        restart: always
        environment:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_USER: user
          MYSQL_PASSWORD: user
          MYSQL_DATABASE: Remates
        volumes:
          - db_data:/var/lib/mysql
        networks:
          - mynetwork 

      web:
        image: gastonnicora/remates-vue
        ports:
          - "80:80"
        restart: always
        depends_on:
          - api
          - socket
        networks:
          - socket
          - conn 

      api:
        image: gastonnicora/remates-python
        restart: always
        environment:
          DB_HOST: db:3306
          DB_USER: user
          DB_PASS: user
          DB_NAME: Remates
          REDIS_HOST: redis
        depends_on:
          - db
          - redis
        ports:
          - "4000:4000"
        networks:
          - mynetwork 
          - conn 
      
      socket:
        image: gastonnicora/remates-socket
        restart: always
        environment:
          REDIS_HOST: redis
        depends_on:
          - api
          - redis
        expose:
          - "4001"
        ports:
          - "4001:4001"
        networks:
          - mynetwork
          - socket 

      celery:
        image: gastonnicora/remates-celery
        restart: always
        depends_on:
          - redis
          - api
        ports:
          - "5555:5555"
        expose:
          - "5000" 
        networks:
          - mynetwork 

      phpmyadmin:
        image: phpmyadmin
        restart: always
        environment:
          PMA_HOST: db
          PMA_PORT: 3306
        ports:
          - "90:80"
        depends_on:
          - db
        networks:
          - mynetwork 

      redis:
        image: redis:7-alpine
        expose:
          - "6379"
        volumes:
          - redis_data:/data
        networks:
          - mynetwork

    networks:
      mynetwork:
      socket:
        driver: bridge 
      conn:
        driver: bridge 

    volumes:
      db_data:
      redis_data: 

    ```

2. **Construye y levanta los contenedores con Docker Compose**:

    Asegúrate de que Docker y Docker Compose estén instalados en tu máquina.

    Ejecuta el siguiente comando para construir y levantar los contenedores necesarios:

    ```bash
    docker-compose up --build 
    ```

    Este comando levantará los siguientes contenedores:

    - **api**: Contenedor que ejecuta la API RESTful.
    - **db**: Contenedor de la base de datos (MySQL).
    - **redis**: Contenedor para el almacenamiento de tareas de Celery y la comunicación entre la API, el WebSocket y Celery
    - **celery**: Contenedor para ejecutar tareas asíncronas.
    - **socket**: Contenedor para gestionar las conexiones WebSocket en tiempo real.
    - **web**: Contenedor con la interfaz de usuario 


3. **Accede a la Flower**:

    Una vez que los contenedores estén levantados, puedes acceder a flower (visualizar tareas):

    ```arduino
    http://localhost:5555
    ```

## Detener los Contenedores
Para detener y eliminar los contenedores en ejecución, ejecuta el siguiente comando:

```bash
docker-compose down
```
Si deseas eliminar también los volúmenes, usa la opción ``-v``:

```bash
docker-compose down -v
```

## Tareas
Celery se encarga de recibir tareas desde la cola de Redis y ejecutar ciertas funciones cuando sea el momento adecuado. En este caso, las tareas se activan mediante un intervalo de tiempo determinado y luego se realizan solicitudes HTTP a la API para completar las acciones.


  - **Eliminar confirmación de email**:
    ```
      Tarea: deleteConfirm_as
      Descripción: Luego de 24hs hace una petición a API para que elimine la confirmación de email y el usuario
    ```

  - **Finalizar Articulo**:
    ```
      Tarea: taskFinishedArticle
      Descripción: Luego de un tiempo definido por API se le pide a la misma que finalize la subasta de un articulo
    ```
  - **Comenzar Articulo**:
    ```
      Tarea: taskStartedArticle
      Descripción: Luego de un tiempo definido por API se le pide a la misma que comience la subasta de un articulo
    ```
  - **Finalizar Subasta**:
    ```
      Tarea: taskFinishedAuction
      Descripción: Cuando llega el momento de finalización definido por API se le pide a la misma que comience la subasta de un articulo
    ```
  - **Comenzar Articulo**:
    ```
      Tarea: taskStartedAuction
      Descripción: Cuando llega el momento de comienzo definido por API se le pide a la misma que comience la subasta de un articulo
    ```
## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE.md) para más detalles.

## Contacto
- Email: gastonmatias.21@gmail.com
- Teléfono: 2345453976