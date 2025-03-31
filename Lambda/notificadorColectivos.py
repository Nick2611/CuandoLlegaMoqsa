import os
import boto3 

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from tempfile import mkdtemp

from selenium.webdriver.support.wait import WebDriverWait

sns_client = boto3.client('sns')  
sns_topic_arn = os.environ['SNS_TOPIC_ARN']  


def lambda_handler(event, context):
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"
    url = 'https://cuandollega.smartmovepro.net/moqsa/arribos/?codLinea=92&idParada=MO-01076'

    service = Service(
        executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver", 
        service_log_path="/tmp/chromedriver.log"
    )

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    try:
        driver.get(url)

        try:
            container = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, 'arribosContainer'))
            )
            sub_elements = container.find_elements(By.CLASS_NAME, "mdl-card--horizontal")

            tiemposLlegada = []
            for element in sub_elements:
                datosLlegada = str(element.text).split("\n")
                tiempoLlegada = datosLlegada[2]
                tiemposLlegada.append(tiempoLlegada)

            if not tiemposLlegada:
                mensaje = "No hay colectivos en camino"
            else:
                mensaje = f"Los colectivos llegaran en:\n\n"
                for tiempo in tiemposLlegada:
                    mensaje += f"{tiempo}\n"

        except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.NoSuchElementException):
            mensaje = "No hay colectivos en camino."
            print(mensaje)

        except Exception as e:
            mensaje = f"An unexpected error occurred: {e}"
            print(mensaje)

    except Exception as e:
        mensaje = f"Error during lambda execution: {e}"
        print(mensaje)

    finally:
        if 'driver' in locals():
            driver.quit()

    try:
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=mensaje,
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'LambdaAlert'  
                }
            }
        )
        print(f"SNS Publish Response: {response}")
    except Exception as sns_error:
        print(f"Error publishing to SNS: {sns_error}")

    return {
        'statusCode': 200,
        'body': mensaje,
    }
