# [HOW TO] AWS AI 서비스들을 활용한 국내 헬스케어 비정형 데이터의 정형화

## 주의: 본 데모에 포함된 데이터는 모두 직접 작성 및 녹음된 가상의 데이터입니다. 본 데모를 활용 시 실제 의료 데이터를 사용하고자 할 때는, 반드시 개인정보 및 관련 국내법 등을 준수하여 사용하세요. 

본 데모는 Amazon Bedrock의 Claude 3 Haiku 모델과 Amazon Transcribe를 통해 비정형 의료 데이터, 그 중에서도 음성 및 텍스트를 간단하게 정형화할 수 있음을 제안합니다. 
Claude 모델, 그 중에서도 Haiku 모델은 높은 성능과 매우 빠른 처리 속도, 적은 비용이 장점인 모델로, 이를 활용하면 기존에 어렵던 비정형 텍스트 및 음성 데이터를 빠르고 비용 효율적으로 처리할 수 있습니다. 

한국어 음성 데이터의 경우 STT AI 서비스인 Amazon Transcribe가 이를 전사 처리 해줍니다. 
이렇게 텍스트 형태로 처리된 음성 데이터, 그리고 진료기록지 같은 텍스트 데이터는 Amazon Bedrock의 여러 모델 중 한국어를 지원하는 Claude 3 Haiku 모델이 정형화 작업을 해주게 됩니다.
정형화된 데이터는 nosql 데이터베이스인 Amazon DynamoDB, 그리고 Amazon Opensearch에 각각 적재됩니다. 

사용자는 자신의 AWS 계정에서 본 데모의 CDK를 배포하기만 하면 됩니다. CDK를 통해 배포된 S3 버킷에 자신이 원하는 데이터, 혹은 함께 동봉된 샘플 데이터를 업로드만 하면 됩니다.
이를 통해 사용자는 기존에 처리하기 어려웠던 복잡한 의료 데이터가 AI를 통해 자동으로 정형화 작업이 되는 것을 확인할 수 있습니다. 

## Architecture

![Image (6)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/2bb6a178-b48e-4043-92a6-30373e25a34f)

1. 음성 의료 데이터는 STT ML 서비스인 Amazon Transcribe를 통해서 전사되어 처리됩니다.
2. 텍스트 데이터는 그대로 처리 됩니다.
3. 두 데이터는 모두 Amazon Bedrock의 Claude 3.0 Haiku 모델을 통해 사전에 미리 프롬프트 상에서 정의한 분류로 데이터가 정제되어 DynamoDB에 저장되게 됩니다.



## Example 1: 간에 대한 진료 기록지 처리 결과

<img width="729" alt="Screenshot 2024-04-15 at 11 56 18 PM" src="https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/089ed559-0820-4d76-a0a5-994c275ffcea">

위와 같은 진료기록지는 S3에 저장됨과 동시에 MedicalBedrock 이름의 AWS Lambda 함수로 Bedrock API 호출을 하여 처리 됩니다. 
실제 처리된 결과는 다음과 같습니다. 

|DiagnosisID|Age|Anatomy|Date|Diagnosis and Conditions|Future Plans|Observations and Findings|Symptoms and Signs|Tests and Examinations|Treatments and Medications|Summary|
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
|0065b095-e083-4aaf-992e-5523b4f231d1|60|간|2023-10-20|만성 간염 가능성|	추가적인 간 기능 검사 및 바이러스 항원 검사 예정|간기능검사 결과 AST 50 U/L, ALT 45 U/L로 약간 상승, 혈액 내 알부민 3.5 g/dL, 간 초음파 상 간 크기 정상, 간내 담석 의심 없음|지속적인 피로감, 식욕 부진, 간통, 소화 불량, 체중 감소"|"혈액 검사(간염 검사, 간기능검사, 혈액 내 알부민, 혈액 내 전형적인 전자 수), 간 초음파|건강한 식습관과 적절한 휴식 유지 권고 |60세 여성 환자가 최근 3개월 동안 지속적인 피로감, 식욕 부진, 간통, 소화 불량, 체중 감소 증상을 보이고 있습니다. 혈액 검사와 간 초음파 결과 만성 간염 가능성이 있어 추가 검사를 진행할 예정입니다.|

## Example 2: 피부 관련 진료 기록지 처리 결과 

<img width="904" alt="Screenshot 2024-04-16 at 12 09 55 AM" src="https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/c712b815-7305-4a67-a56d-154d4b4cefcb">

위와 같은 진료기록지 역시 S3에 저장됨과 동시에 MedicalBedrock 이름의 AWS Lambda 함수로 Bedrock API 호출을 하여 처리 됩니다.
실제 처리 결과는 다음과 같습니다. 

|DiagnosisID|Age|Anatomy|Date|Diagnosis and Conditions|Future Plans|Observations and Findings|Symptoms and Signs|Tests and Examinations|Treatments and Medications|Summary|
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
|5fb9aec2-7b48-48bf-894a-fcb8e00e1588|29|"얼굴, 팔"|2023-11-25|피부염(피부 질환)|피부 상태 지속 관찰, 재방문 시 평가, 필요 시 치료 계획 조정 |	얼굴과 팔에 거칠고 붉은 반점|가려움증, 통증, 건조한 피부, 붉은 반점|피부 조직 검사, 알레르기 패치 테스트|보습제, 스테로이드 크림, 영양 보충, 식습관 교정|29세 남성 환자가 얼굴과 팔에 가려움증, 통증, 건조한 피부, 붉은 반점 등의 증상을 보여 피부염으로 진단되었습니다. 피부 조직 검사와 알레르기 패치 테스트를 실시하고 보습제, 스테로이드 크림, 영양 보충, 식습관 교정 등의 치료를 받게 됩니다. 향후 피부 상태를 지속적으로 관찰하고 재방문 시 평가하여 필요한 경우 치료 계획을 조정할 예정입니다.|

본 데모를 배포하시면 원하는 오디오 및 텍스트 파일에 대한 테스트가 가능합니다. 

## 배포 전 준비사항

1. AWS 콘솔 상에서 Bedrock의 Model Access에서 Anthropic의 Claude를 활성화해주세요.
2. AWS CLI 설정: 아직 하지 않으셨다면, aws cli를 설정해주세요. '''aws configure''' 를 통해 손쉽게 하실 수 있습니다.
3. AWS CLI 설정 시 기본 리전을 반드시 Bedrock, 그 중에서도 Claude 모델이 활성화가 되어 있는 리전에서 사용해주세요.

## 배포 방법

1. Download github source

```
$ git clone https://github.com/ltrain81/korean-emrdata-aws-demo.git
```

2. Install Dependencies

```
$ pip install -r requirements.txt
```

3. cdk bootstrap

```
$ cdk bootstrap
```

4. cdk deploy

```
$ cdk deploy
```


## 사용 방법 

1. 위의 방법으로 배포할 시 다음과 같은 리소스들이 생성됩니다.
    1. 1 Amazon S3 Bucket (mab-{계정ID}-{리전코드})
    2. 4 AWS Lambdas 
    3. 1 Amazon DynamoDB Tables (MedicalTable)
    4. 4 IAM Roles
    5. 1 Amazon Opensearch Domain
    6. 2 AWS Lambda Layers
    7. Amazon S3에는 다음과 같이 두 개의 경로가 생성됩니다. 

![Image (7)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/276ee4cc-2533-407a-bf0d-80d1021b0177)

2. 음성 데이터

* 현재 mp3 파일만 지원합니다.
* audioEMR 안에 있는 raw-audio 경로 안에 원하는 mp3 파일을 집어 넣습니다.

![Image (8)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/5fca0d49-8bdd-4a39-aaf1-2432b860fa20)


3. 텍스트 데이터

* 텍스트 데이터의 경우, txt 파일만을 지원합니다.
* textEMR 경로에 원하는 txt 파일을 집어넣습니다. 

![Image (9)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/faf943e1-dd55-448f-a6e0-9006bd559d1f)


4. 결과 확인: 이외 처리 작업은 모두 자동화 되어 있습니다. 처리 결과는 두 가지 방법으로 확인할 수 있습니다.

* Amazon DynamoDB: MedicalTable 이름으로 생성된 DynamoDB 테이블에서 처리 결과 확인

![Image (10)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/98f8332f-148e-4a7e-af69-f41c573f7655)

* Amazon Opensearch: 처리된 데이터가 적재된 Amazon Opensearch에서 검색 및 시각화

![Image (11)](https://github.com/ltrain81/korean-emrdata-aws-demo/assets/63511851/7cc3460b-ef61-4345-b3a0-7a7703c5455f)

## 샘플 데이터 활용

본 데모에서는 Patients 폴더 안에 여러 텍스트 및 오디오 샘플 데이터가 있습니다.
해당 데이터는 모두 가상의 데이터이므로, 학습 및 연구 목적에 적합하지는 않지만, 동시에 자유롭게 테스트 해볼 수 있습니다.
해당 데이터를 S3에 업로드하면서 본 데모를 시작해보세요. 

## 프롬프트 변경하기 

본 데모는 AWS Lambda를 활용하고 있습니다. 
본 데모를 활용하면서 기존과 다른 방식의 정형화를 시도하고자 하는 분들은 MedicalAnalysisStack-MedicalBedrock~ 이라는 이름의 Lambda 함수 내에서 프롬프트를 수정할 수 있습니다.
수정 시, 프롬프트에 따라 헬스케어와 무관한 모든 도메인의 데이터 역시 처리가 가능하며 테스트 해볼 수 있습니다. 
다만 이 경우, 필요에 따라 자동으로 생성된 DynamoDB의 Primary Key를 변경해야할 수 있습니다. 



