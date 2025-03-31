CuandoLlegaMoqsa

Que es Moqsa
Moqsa, de acuerdo con Moovit, es un proveedor de transporte publico en Buenos Aires que opera rutas de Colectivo. Actualmente cuenta con 22 rutas en Buenos Aires con 1526 paradas de colectivo, convirtiendola en una de las lineas mas utilizadas de toda el AMBA (Area Metropolitana de Buenos Aires)

Para mayor comodidad de sus pasajeros, la compañía cuenta con una página web que informa en tiempo real cuánto falta para que el colectivo llegue a cada parada, permitiendo a los usuarios organizar mejor sus tiempos y planificar sus viajes de manera más eficiente.

La problemática que aborda este programa surge del hecho de que la página de Moqsa no ofrece ninguna opción para notificar a los usuarios cuando el colectivo está cerca de su parada. Esto puede generar inconvenientes, especialmente cuando una persona esta distraída y ocupada con otras actividades, aumentando el riesgo de que pierda su colectivo por no estar atenta a su llegada.



Arquitectura de AWS
Aunque se trata de una solución sencilla, se busca implementar una arquitectura que permita la ejecución automática de la función en intervalos definidos por el usuario, tantas veces como sea necesario. Además, se procura minimizar el uso de servicios para optimizar costos y facilitar su comprensión.
Listado de servicios utilizados:
Amazon EventBridge Scheduler: Servicio que permite programar la ejecución de tareas en momentos específicos o en intervalos regulares. En este caso, se usa para activar la función Lambda en el horario definido.


AWS Lambda: Servicio de computación sin servidor que ejecuta código en respuesta a eventos. En este caso, se utiliza para realizar la tarea de web scraping y obtener los datos necesarios.


Amazon CloudWatch Logs: Servicio que recopila, monitorea y almacena registros generados por diferentes servicios de AWS. Se usa para registrar la ejecución de la función Lambda y depurar posibles errores.


Amazon SNS (Simple Notification Service) Topic: Servicio de mensajería que permite enviar notificaciones a múltiples suscriptores a través de diferentes protocolos (correo electrónico, SMS, etc.). En este caso, se usa para enviar los datos obtenidos a los usuarios por correo electrónico.

Todos estos servicios se conectan de manera sincronizada para llevar a cabo el proposito del programa

Estructura de la función Lambda
El script que corre en la funcion lambda es el siguiente:
<vinculo al archivo>

Realiza un simple Scraping de datos presentes en el sitio web de Moqsa, se busca localizar el container que contiene los N arribos proximos. Dicho container se encuentra en la siguiente ubicacion dentro del HTML de la pagina

<div id="arribosContainer" class="mdl-cell mdl-cell--12-col" style="display: inline-block;
            margin-left: 0;
            width: 100%;
            max-width: 600px;">
</div>

Dentro de los container se hallaran los proximos arribos del ramal elegido, informacion que se busca convertir para añadir al mensaje final que devuelve la funcion.

Notas importantes:
El ARN (Amazon Resource Name, identificador unico de los topicos SNS) del topico se encuentra especificado como variable de entorno 


Los paths de instalacion estan especificador en el bash de instalacion de chrome y chromedriver, script el cual se abordara mas adelante en el documento


Docker, instalación de chrome con Bash, push a ECR
Como lambda no cuenta con los requisitos para que la libreria utilizada para el scrape (Selenium) funcione, es necesario utilizar Docker para poder instalar Chrome y ChromeDriver

La estructura del archivo Docker es la siguiente:
FROM amazon/aws-lambda-python:3.12
# Install chrome dependencies
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
   libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
   libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
   xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip
# Copy and run the chrome installer script
COPY ./chrome-installer.sh ./chrome-installer.sh
RUN chmod +x ./chrome-installer.sh
RUN ./chrome-installer.sh
RUN rm ./chrome-installer.sh
# Install selenium
RUN pip install selenium
# Copy the main application code
COPY notificadorColectivos.py ./
# Command to run the Lambda function
CMD [ "notificadorColectivos.lambda_handler" ]

Se utilizan una serie de comandos que ejecutan distintas acciones:
FROM - Importa la imagen de amazon a utilizar con la versión de python utilizada
DNF -  Instala las dependencias a utilizar para ejecutar Chrome y Selenium

Las siguientes 4 lineas son comandos relacionadas a la instalacion de Google Chrome y la asignacion de los permisos necesarios para ejecutar el bash
COPY ./chrome-installer.sh ./chrome-installer.sh
RUN chmod +x ./chrome-installer.sh
RUN ./chrome-installer.sh
RUN rm ./chrome-installer.sh

Finalmente, se realiza la instalacion de Selenium, la copia del codigo de la aplicación (Script notificadorColectivos.py) al contenedor y se define el punto de entrada para Lambda, que ejecutara la funcion Lambda_handler dentro del script
RUN pip install selenium
# Copy the main application code
COPY notificadorColectivos.py ./
# Command to run the Lambda function
CMD [ "notificadorColectivos.lambda_handler" ]

Por otro lado, la estructura del archivo bash chrome-installer.sh se da de la siguiente manera:

#!/bin/bash
set -e


chrome_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chrome-linux64.zip"
chromedriver_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chromedriver-linux64.zip"


download_path_chrome_linux="/opt/chrome-linux64.zip"
download_path_chrome_driver_linux="/opt/chromedriver-linux64.zip"


mkdir -p "/opt/chrome"
curl -Lo "$download_path_chrome_linux" "$chrome_linux_url"
unzip -q "$download_path_chrome_linux" -d "/opt/chrome"
rm -rf "$download_path_chrome_linux"


mkdir -p "/opt/chromedriver"
curl -Lo "$download_path_chrome_driver_linux" "$chromedriver_linux_url"
unzip -q "$download_path_chrome_driver_linux" -d "/opt/chromedriver"
rm -rf "$download_path_chrome_driver_linux"
chmod +x "/opt/chromedriver/chromedriver-linux64/chromedriver"

Aqui una explicación sobre los componentes del script:

Se indica que el script debe ejecutarse en Bash y se hace que el script se detenga inmediatamente si ocurre un error en cualquier línea

#!/bin/bash
set -e	


Se definen las URL tanto de descarga como de almacenamiento temporal antes de ser extraidos
chrome_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chrome-linux64.zip"
chromedriver_linux_url="https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.90/linux64/chromedriver-linux64.zip"


download_path_chrome_linux="/opt/chrome-linux64.zip"
download_path_chrome_driver_linux="/opt/chromedriver-linux64.zip"


Se extraen e instalan los archivos correspondientes a Google Chrome
mkdir -p "/opt/chrome"
curl -Lo "$download_path_chrome_linux" "$chrome_linux_url"
unzip -q "$download_path_chrome_linux" -d "/opt/chrome"
rm -rf "$download_path_chrome_linux"

Se repite el paso anterior pero en esta ocasión para ChromeDriver y se le asignan los permisos correspondientes
mkdir -p "/opt/chromedriver"
curl -Lo "$download_path_chrome_driver_linux" "$chromedriver_linux_url"
unzip -q "$download_path_chrome_driver_linux" -d "/opt/chromedriver"
rm -rf "$download_path_chrome_driver_linux"
chmod +x "/opt/chromedriver/chromedriver-linux64/chromedriver"

Push a ECR
Se utilizaron los comandos recomendados por la documentación oficial de AWS para realizar el push de la imagen Docker del script a Amazon Elastic Container Registry (ECR). Sin embargo, se presentó un problema recurrente que impedía la correcta adopción de la imagen por la función AWS Lambda.
Descripción del problema y solución
Al realizar el push, la imagen se subía de manera fragmentada a ECR, lo que resultaba en:
Una imagen que aparecía con un tamaño menor al esperado.


División en tres partes, lo que impedía su correcto uso en AWS Lambda.
Para solucionar este problema, se implementó el siguiente comando antes del build de la imagen:
$env:DOCKER_BUILDKIT = "0"
Este comando deshabilita Docker BuildKit temporalmente en la sesión actual, lo que permitió que la imagen se subiera correctamente a ECR. Es probable que la problemática estuviera relacionada con errores de compatibilidad entre BuildKit y los distintos comandos utilizados.
Gracias a esta solución, la imagen pudo ser adoptada sin inconvenientes por AWS Lambda.
Comandos utilizados
Crear un repositorio en Amazon ECR: Este comando crea un repositorio en Amazon ECR donde almacenarás las imágenes Docker. Especifica el nombre del repositorio y la región de AWS.


aws ecr create-repository --repository-name <nombre-repositorio> --region <nombre-región>
--repository-name: Especifica el nombre del repositorio que deseas crear.


--region: Especifica la región en la que se creará el repositorio (por ejemplo, us-east-1).



Construir una imagen Docker: Este comando construye una imagen Docker a partir de un Dockerfile presente en el directorio actual.


docker build -t <nombre-repositorio> .
-t <nombre-repositorio>: Asigna un nombre a la imagen Docker construida.


.: Indica que Docker debe usar el archivo Dockerfile en el directorio actual para construir la imagen.



Etiquetar la imagen Docker con la URL del repositorio ECR: Después de construir la imagen, debes etiquetarla para que apunte al repositorio de ECR donde deseas subirla.


docker tag <nombre-imagen> <aws-account-id>.dkr.ecr.<region>.amazonaws.com/<nombre-repositorio>:latest
<nombre-imagen>: Es el nombre de la imagen Docker que acabas de construir.


<aws-account-id>: El ID de tu cuenta de AWS.


<region>: La región de AWS en la que resides (por ejemplo, us-east-1).


<nombre-repositorio>: El nombre del repositorio en ECR.


:latest: La etiqueta de la imagen (puedes usar otro tag si prefieres).



Obtener el token de inicio de sesión de ECR y hacer login: Este comando obtiene el token de acceso para autenticarte en tu repositorio ECR.


(Get-ECRLoginCommand).Password | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
(Get-ECRLoginCommand).Password: Obtiene el token de inicio de sesión desde AWS CLI.


docker login --username AWS --password-stdin: Usa el token para iniciar sesión en Docker.


<aws-account-id>: El ID de tu cuenta de AWS.


<region>: La región de AWS donde resides (por ejemplo, us-east-1).



Subir la imagen Docker a Amazon ECR: Este comando sube la imagen Docker etiquetada al repositorio en Amazon ECR.


docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/<nombre-repositorio>:latest
<aws-account-id>: El ID de tu cuenta de AWS.


<region>: La región de AWS donde está el repositorio ECR (por ejemplo, us-east-1).


<nombre-repositorio>: El nombre del repositorio en ECR.


:latest: La etiqueta de la imagen (puedes usar otro tag si prefieres).

	

Creacion de regla EventBridge Scheduler

EventBridge se utiliza para la creacion de reglas para realizar tareas programadas que se ejecutaran automaticamente en lambda en momentos especificos que nosotros como usuarios definimos.

Para crear una regla que se adapte, por ejemplo, a una rutina lunes-viernes de 15hs a 16hs, ejecutandose cada 10 minutos:

Paso 1- Crear la función lambda y añadir trigger
Buscando Lambda en la consola de AWS, se nos brindara la opcion de crear una nueva funcion Lambda



Paso 2- Definir parámetros de la función
Para continuar con este paso, debemos haber realizado el push de la Docker image a ECR para poder utilizarla con la funcion Lambda

Elegimos Container Image para asignar la Docker Image a la funcion


Seleccionamos Browse images y elegimos nuestro repositorio de ECR donde esta la imagen de nuestro programa, marcamos la imagen para continuar



