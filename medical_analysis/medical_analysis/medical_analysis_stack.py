from aws_cdk import (
    Stack, 
    App, 
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_opensearchservice as opensearch,
    aws_secretsmanager as secrets,
    aws_s3_notifications as s3event,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    Duration
)
from constructs import Construct
import aws_cdk
import uuid


class MedicalAnalysisStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_id = self.account
        region = self.region
        bucket_name = f"mab-{account_id}-{region}"

        #create S3 bucket and folders
        medicalbucket = s3.Bucket(
            self, 
            "MedicalBucket",
            bucket_name=bucket_name
        )

        #create diretories of S3 by inserting dummy object
        
        raw_audio_folder = s3deploy.BucketDeployment(
            self,
            "raw_audio_folder",
            sources=[s3deploy.Source.asset("./dummy/dummy.zip")],
            destination_bucket=medicalbucket,
            destination_key_prefix="audioEMR/raw-audio"
        )

        text_emr_folder = s3deploy.BucketDeployment(
            self,
            "text_emr_folder",
            sources=[s3deploy.Source.asset("./dummy/dummy.zip")],
            destination_bucket=medicalbucket,
            destination_key_prefix="textEMR"
        )

        #Generate secret and store to AWS Secrets Manager

        opensearch_password = secrets.Secret(self, "Opensearch_Password")
        opensearch_username = "admin"
        advanced_security_config = opensearch.AdvancedSecurityOptions(
            master_user_name=opensearch_username,
            master_user_password=opensearch_password.secret_value
        )

        '''
        #Configure Opensearch
        OPENSEARCH_VERSION = "2.11"

        encryption_config = opensearch.EncryptionAtRestOptions(
            enabled=True
        )

        capacity_config = opensearch.CapacityConfig(
            master_nodes=3,
            master_node_instance_type="m4.large.search",
            data_nodes=3,
            data_node_instance_type="m4.large.search",
            warm_nodes=0
        )

        zone_awareness_config = opensearch.ZoneAwarenessConfig(
            availability_zone_count=3,
            enabled=True
        )

        ebs_config = opensearch.EbsOptions(
            volume_size=10,
            volume_type=aws_cdk.aws_ec2.EbsDeviceVolumeType.GP2
        )

        medical_opensearch = opensearch.Domain(
            self, "MedicalDomain",
            version=opensearch.EngineVersion.open_search(OPENSEARCH_VERSION),
            node_to_node_encryption=True,
            capacity=capacity_config,
            ebs=ebs_config,
            enforce_https=True,
            encryption_at_rest=encryption_config,
            fine_grained_access_control=advanced_security_config,
            zone_awareness=zone_awareness_config
        )

        opensearchURL = medical_opensearch.domain_endpoint

        aws_cdk.CfnOutput(self,"OpenSearchDomainEndpoint", value=medical_opensearch.domain_endpoint)
        aws_cdk.CfnOutput(self,"OpenSearchDashboardsURL", value=(medical_opensearch.domain_endpoint + "/_dashboards"))
        aws_cdk.CfnOutput(self,"OpenSearchPasswordSecretName", value=opensearch_password.secret_name)
        aws_cdk.CfnOutput(self,"OpenSearchAdminUser", value=opensearch_username)
        '''

        #dynamoDB table Build
        medical_table = dynamodb.Table(
            self, "MedicalTable",
            partition_key=dynamodb.Attribute(
                name="DiagnosisID",
                type=dynamodb.AttributeType.STRING
            )
        )

        #Lambda Layers 
        boto3_mylayer = _lambda.LayerVersion(
            self, "Boto3MyLayer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_7,
                _lambda.Runtime.PYTHON_3_8,
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10
            ],
            code=_lambda.Code.from_asset("./lambda/boto3-mylayer.zip")
        )

        requests_layer = _lambda.LayerVersion(
            self, "RequestLayer",
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_7,
                _lambda.Runtime.PYTHON_3_8,
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10
            ],
            code=_lambda.Code.from_asset("./lambda/requests.zip")
        )

        #IAM Roles for Lambda
        audio_to_transcribe_role = iam.Role(
            self, "AudioToTranscribeRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="AudioToTranscribeLambdaRole"
        )

        transcript_to_txt_role = iam.Role(
            self, "TranscriptToTxtRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="TranscriptToTxtRole",
        )

        medical_bedrock_role = iam.Role(
            self, "MedicalBedrockRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="MedicalBedrockRole",
        )

        ''''
        ddb_to_opensearch_role = iam.Role(
            self, "DDBtoOpensearchRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="DDBtoOpensearchRole",
        )
        '''
        audio_to_transcribe_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        audio_to_transcribe_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonTranscribeFullAccess'))
        audio_to_transcribe_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        transcript_to_txt_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        transcript_to_txt_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        medical_bedrock_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))
        #ddb_to_opensearch_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonOpenSearchServiceFullAccess'))
        #ddb_to_opensearch_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))

        #4 Lambda Functions
        audio_to_transcribe_code_path = "./lambda/AudioToTranscribe.zip"
        audio_to_transcribe_lambda = _lambda.Function(
            self, "AudioToTranscribe",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset(audio_to_transcribe_code_path),
            role=audio_to_transcribe_role,
            timeout=aws_cdk.Duration.minutes(3)
        )

        # Create Lambda function for TranscriptToTxt
        transcript_to_txt_lambda_code_path = "./lambda/TranscriptToTxt.zip"
        transcript_to_txt_lambda = _lambda.Function(
            self, "TranscriptToTxt",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset(transcript_to_txt_lambda_code_path),  # Replace with your path
            timeout=aws_cdk.Duration.minutes(3),
            role=transcript_to_txt_role,  # Assign the previously defined IAM role
        )

        medical_bedrock_path = "./lambda/medical-bedrock.zip"
        medical_bedrock_lambda = _lambda.Function(
            self, "MedicalBedrock",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset(medical_bedrock_path),  # Replace with your path
            timeout=aws_cdk.Duration.minutes(3),
            role=medical_bedrock_role,  # Assign the previously defined IAM role
            layers=[boto3_mylayer]
        )

        ''''
        ddb_to_opensearch_path = "./lambda/DDBtoOpensearch.zip"
        ddb_to_opensearch_lambda = _lambda.Function(
            self, "DDBtoOpensearch",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset(ddb_to_opensearch_path),  # Replace with your path
            timeout=aws_cdk.Duration.minutes(3),
            role=ddb_to_opensearch_role,  # Assign the previously defined IAM role
            environment={
                "Opensearch_Username": "admin",
                "Opensearch_URL": opensearchURL,
                "Opensearch_Password": str(opensearch_password.secret_value)
            },
            layers=[requests_layer]
        )
        '''
        #S3 Event Notifications + DDB Stream


        #DDB Stream to Put Later
        # ***PUT DDB Stream here

def main():    
    app = App()
    MedicalAnalysisStack(app, "MedicalAnalysisStack")
    app.synth()

if __name__ == "__main__":
    main()
