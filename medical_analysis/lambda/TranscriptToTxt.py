import boto3
import json

def lambda_handler(event, context):
    # Extract bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    source_file_key = event['Records'][0]['s3']['object']['key']
    
    if source_file_key.endswith('.json'):
        # Get the transcription result
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=source_file_key)
        transcription_result = json.load(response['Body'])
        
        transcript = transcription_result['results']['transcripts'][0]['transcript']
        
        # Save transcript to a text file in the 'transcript-txt' folder
        output_key = source_file_key.replace('transcribe-output', 'transcript-txt').replace('.json', '.txt')
        output_file_path = f"/tmp/{output_key.split('/')[-1]}"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(transcript)
        
        # Upload the text file to S3
        s3_client.upload_file(output_file_path, bucket_name, output_key)
        
        return {
            'statusCode': 200,
            'body': 'Transcript extracted and saved as a text file.'
        }
    else:
        return {
            'statusCode': 400,
            'body': 'Unexpected file format or key.'
        }
