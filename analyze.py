from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import time
import os

#Run the following lines from 8-14 to load the environment variables from the .env file which is a very common usage.
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# endpoint = os.getenv("Endpoint")
# key = os.getenv("Key")

# If you don't want to use the .env file, you can use a .json file to declare the endpoint and the key. But don't forget to add the .json file to the .gitignore file.
import json

with open('config.json') as config_file:
    config = json.load(config_file)

endpoint = config["Endpoint"]
key = config["Key"]


if not endpoint or not key:
    raise EnvironmentError("Azure credentials not set in environment variables")

credentials = CognitiveServicesCredentials(key)

client = ComputerVisionClient(
    endpoint=endpoint,
    credentials=credentials
)

def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    # SDK call
    rawHttpResponse = client.read(uri, language="en", raw=True)

    # Get ID from returned headers
    operationLocation = rawHttpResponse.headers["Operation-Location"]
    idLocation = len(operationLocation) - numberOfCharsInOperationId
    operationId = operationLocation[idLocation:]

    # SDK call
    result = client.get_read_result(operationId)
    
    # Try API
    retry = 0
    
    while retry < maxRetries:
        if result.status.lower () not in ['notstarted', 'running']:
            break
        time.sleep(1)
        result = client.get_read_result(operationId)
        
        retry += 1
    
    if retry == maxRetries:
        return "max retries reached"

    if result.status == OperationStatusCodes.succeeded:
        res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
        return res_text
    else:
        return "error"
