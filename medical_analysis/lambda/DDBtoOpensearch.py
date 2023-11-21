import json
import requests
import os

def lambda_handler(event, context):
    if "NewImage" in event["Records"][0]['dynamodb']:
        item = event["Records"][0]['dynamodb']['NewImage']
        
        # Extracting data from DynamoDB NewImage
        result = {}
        for key, value in item.items():

            result[key] = list(value.values())[0]
        
        # Constructing the OpenSearch document
        document = {
            "data": result  # Assuming you want to nest the DynamoDB data under a 'data' field
        }
        
        opensearch_url = os.environ['Opensearch_URL']
        index_name = "patients"
        datatype = "_doc"
        url = f"{opensearch_url}/{index_name}/{datatype}"
        headers = { "Content-Type": "application/json" }
        
        user = os.environ['Opensearch_Username']
        password = os.environ['Opensearch_Password']
        
        auth = requests.auth.HTTPBasicAuth(user, password)
        
        try:
            response = requests.post(url, auth=auth, json=document, headers=headers)
            response.raise_for_status()
            print(f"Document indexed: {response.json()}")
        except requests.exceptions.HTTPError as err:
            print(f"Failed to index document: {err}")
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
        print("New data added?!")

    else:
        print("no NewImage")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }