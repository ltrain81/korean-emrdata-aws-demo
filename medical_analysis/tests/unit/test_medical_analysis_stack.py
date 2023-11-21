import aws_cdk as core
import aws_cdk.assertions as assertions

from medical_analysis.medical_analysis_stack import MedicalAnalysisStack

# example tests. To run these tests, uncomment this file along with the example
# resource in medical_analysis/medical_analysis_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MedicalAnalysisStack(app, "medical-analysis")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
