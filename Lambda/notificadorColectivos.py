import os
import boto3  # Import Boto3 for AWS services

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support import expected_conditions as EC
from tempfile import mkdtemp

from selenium.webdriver.support.wait import WebDriverWait

# Initialize the SNS client
sns_client = boto3.client('sns')
sns_topic_arn = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    """
    AWS Lambda handler function to scrape bus arrival times and send notifications via SNS.

    Args:
        event (dict): Event data passed by AWS Lambda.
        context (object): Runtime information provided by AWS Lambda.

    Returns:
        dict: Response containing the status code and message body.
    """
    # Set Chrome options for headless browsing
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

    # Set up ChromeDriver service
    service = Service(
        executable_path="/opt/chromedriver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log"
    )

    # Initialize the WebDriver
    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    try:
        # Navigate to the URL
        driver.get(url)

        try:
            # Wait for the container element to be present
            container = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, 'arribosContainer'))
            )
            # Find sub-elements containing arrival times
            sub_elements = container.find_elements(By.CLASS_NAME, "mdl-card--horizontal")

            tiemposLlegada = []
            for element in sub_elements:
                datosLlegada = str(element.text).split("\n")
                tiempoLlegada = datosLlegada[2]
                tiemposLlegada.append(tiempoLlegada)

            # Prepare the message based on arrival times
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
        # Ensure the WebDriver is quit
        if 'driver' in locals():
            driver.quit()

    try:
        # Publish the message to SNS
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
