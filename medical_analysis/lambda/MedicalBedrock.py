import json
import boto3
import csv
import uuid

s3 = boto3.client('s3')
bedrock = boto3.client(service_name='bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
medical_table = dynamodb.Table('MedicalTable')


def lambda_handler(event, context):
    # TODO implement
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    source_file_key = event['Records'][0]['s3']['object']['key']
    response = s3.get_object(Bucket=bucket_name, Key=source_file_key)
    clinical_note = response['Body'].read().decode('utf-8')
    unique_id = str(uuid.uuid4())
    
    prompt = f"""\n\nHuman: 
    
Here is a clinical note written by a doctor in Korean.
You should analyze the note and give me output as below JSON format. 

{{
  "Anatomy": "",
  "Age": "",
  "Date": "",
  "Symptoms and Signs": "",
  "Diagnosis and Conditions": "",
  "Tests and Examinations": "",
  "Treatments and Medications": "",
  "Procedures": "", 
  "Observations and Findings": "",
  "Future Plans": "",
  "Summary": ""
}}

Anatomy: body where the patient is having pain. Always include this. Infer from the context if needed. 
Age: Delete anything other than numbers. 
Date: #YYYY-MM-DD Format Only. Rephrase if needed.
Symptoms and Signs: includes reported symptoms and observed signs by the physician
Diagnosis and Conditions: diagnosed conditions or diseases mentioned in the note.
Tests and Examinations: Any tests or examinations conducted or recommended.
Treatments and Medications: The prescribed treatments, medications, or therapies for the diagnosed conditions.
Procedures": Any medical procedures or interventions discussed or performed. 
Observations and Findings": Any newly observed or documented findings during examinations or tests or while consulting the patient.
Future Plans: Any plans for procedures and Treatments scheduled for future.
Summary: Summarize and delete any personal information such as name, address, ID.

Be concise. 
Never add anything other than JSON above.
Try to use SNOMED-CT terms but translated to Korean. 

Always respond in Korean.

Here is the clinical note: 

{clinical_note}

\n\nAssistant:"""

    body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                    {
                            "content": [
                                    {
                                            "text": prompt,
                                            "type": "text"
                                    }
                            ],
                            "role": "user"
                    }
            ],
            "temperature": 0,
            "top_p": 0
    }

    response = bedrock.invoke_model(
        accept='*/*',
        body=json.dumps(body),
        contentType='application/json',
        modelId='anthropic.claude-3-haiku-20240307-v1:0'
        )
        
    response_body = json.loads(response.get('body').read())
    answer = response_body['content'][0]['text']
    print(answer)
    start_index = answer.find("{")

    analysis = json.loads(answer[start_index:])

    analysis["DiagnosisID"] = unique_id

    medical_table.put_item(Item=analysis)
    print("Note analyzed and added to table successfully")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


